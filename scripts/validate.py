#!/usr/bin/env python3
"""校验 data/topics.json、data/questions.json、data/dependencies.json（仅标准库）。

用法：
    python3 scripts/validate.py [--data-dir DATA_DIR]

默认读取脚本所在目录的 ../data/；--data-dir 可指定其他数据目录。

检查项：
- 知识点：必填字段、id 唯一、term/kind 取值；description 或 mastery 为空只警告。
- 题目：必填字段、id 唯一、topicId 存在、difficulty/type 取值、prompt/answer/explanation 非空；
  choice 题 options 至少 3 项且 answer 须为其中之一；
  numeric 题的 verify 表达式只允许数字与 + - * / ( )，用 ast 安全求值后与 answer 按数值比较。
- 先修边：两端 id 存在、不自指。

全部通过时打印 "VALIDATION PASSED" 并以退出码 0 结束，否则打印错误并以退出码 1 结束。
"""

import argparse
import ast
import json
import os
import sys

TOPIC_FIELDS = ("id", "name", "grade", "term", "unit", "unit_no", "page", "kind")
QUESTION_FIELDS = ("id", "topicId", "difficulty", "type", "prompt", "answer", "explanation")
TERMS = ("上", "下")
KINDS = ("概念", "技能", "活动", "应用")
DIFFICULTIES = ("basic", "medium", "hard")
QUESTION_TYPES = ("numeric", "choice", "text")


def load(data_dir, name, errors):
    path = os.path.join(data_dir, name)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        errors.append(f"{name} 无法读取：{e}")
        return []
    except json.JSONDecodeError as e:
        errors.append(f"{name} 不是合法 JSON：{e}")
        return []
    if not isinstance(data, list):
        errors.append(f"{name} 顶层必须是数组")
        return []
    return data


def _non_empty(value):
    """prompt/explanation/answer 的非空判断：None、空串、纯空白都算空。"""
    if value is None:
        return False
    return str(value).strip() != ""


def _eval_verify(expr):
    """安全求值 verify 表达式。

    只允许数字常量与 + - * / ( )（含一元正负号）。AST 中出现其他任何节点
    （变量名、函数调用、属性访问、幂运算等）一律拒绝，返回 (None, 原因)。
    成功返回 (数值, None)。
    """
    try:
        tree = ast.parse(expr.strip(), mode="eval")
    except SyntaxError as e:
        return None, f"verify 表达式无法解析：{e}"
    allowed = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.USub,
        ast.UAdd,
        ast.Constant,
    )
    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            return None, f"verify 表达式含不允许的成分：{type(node).__name__}"
        if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float)):
            return None, "verify 表达式只允许数字常量"

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.UnaryOp):
            value = _eval(node.operand)
            return -value if isinstance(node.op, ast.USub) else value
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
        raise ValueError(f"不支持的节点：{type(node).__name__}")

    try:
        return _eval(tree), None
    except ZeroDivisionError:
        return None, "verify 表达式除数为零"
    except (ValueError, ArithmeticError) as e:
        return None, f"verify 表达式求值失败：{e}"


def main(argv=None):
    parser = argparse.ArgumentParser(description="校验知识点/题目/先修边数据")
    parser.add_argument(
        "--data-dir",
        default=None,
        help="数据目录（默认：脚本所在目录的 ../data/）",
    )
    args = parser.parse_args(argv)
    if args.data_dir:
        data_dir = args.data_dir
    else:
        data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
        )

    errors = []
    warnings = []
    topics = load(data_dir, "topics.json", errors)
    questions = load(data_dir, "questions.json", errors)
    deps = load(data_dir, "dependencies.json", errors)

    topic_ids = set()
    for i, t in enumerate(topics):
        if not isinstance(t, dict):
            errors.append(f"topics[{i}] 不是对象")
            continue
        for field in TOPIC_FIELDS:
            if field not in t:
                errors.append(f"topics[{i}] 缺字段 {field}")
        tid = t.get("id")
        if tid in topic_ids:
            errors.append(f"topics[{i}] id 重复：{tid}")
        topic_ids.add(tid)
        if t.get("term") not in TERMS:
            errors.append(f"topics[{i}] term 非法：{t.get('term')}")
        if t.get("kind") not in KINDS:
            errors.append(f"topics[{i}] kind 非法：{t.get('kind')}")
        if not _non_empty(t.get("description")):
            warnings.append(f"topics[{i}]（{tid}）description 为空")
        mastery = t.get("mastery")
        if not isinstance(mastery, list) or not mastery:
            warnings.append(f"topics[{i}]（{tid}）mastery 为空")

    question_ids = set()
    for i, q in enumerate(questions):
        if not isinstance(q, dict):
            errors.append(f"questions[{i}] 不是对象")
            continue
        for field in QUESTION_FIELDS:
            if field not in q:
                errors.append(f"questions[{i}] 缺字段 {field}")
        qid = q.get("id")
        if qid in question_ids:
            errors.append(f"questions[{i}] id 重复：{qid}")
        question_ids.add(qid)
        if q.get("topicId") not in topic_ids:
            errors.append(f"questions[{i}] topicId 不存在：{q.get('topicId')}")
        if q.get("difficulty") not in DIFFICULTIES:
            errors.append(f"questions[{i}] difficulty 非法：{q.get('difficulty')}")
        qtype = q.get("type")
        if qtype not in QUESTION_TYPES:
            errors.append(f"questions[{i}] type 非法：{qtype}")
        for field in ("prompt", "answer", "explanation"):
            if field in q and not _non_empty(q.get(field)):
                errors.append(f"questions[{i}]（{qid}）{field} 为空")
        if qtype == "choice":
            options = q.get("options")
            if not isinstance(options, list) or len(options) < 3:
                errors.append(f"questions[{i}]（{qid}）choice 题 options 须为至少 3 项的数组")
            elif _non_empty(q.get("answer")) and str(q.get("answer")).strip() not in [
                str(o).strip() for o in options
            ]:
                errors.append(f"questions[{i}]（{qid}）choice 题 answer 不在 options 中")
        if qtype == "numeric":
            verify = q.get("verify")
            if isinstance(verify, str) and verify.strip():
                value, reason = _eval_verify(verify)
                if reason is not None:
                    errors.append(f"questions[{i}]（{qid}）{reason}")
                else:
                    try:
                        expected = float(str(q.get("answer")).strip())
                    except (TypeError, ValueError):
                        errors.append(
                            f"questions[{i}]（{qid}）numeric 题 answer 无法解析为数字"
                        )
                    else:
                        if abs(value - expected) > 1e-9:
                            errors.append(
                                f"questions[{i}]（{qid}）verify 结果 {value} 与 answer "
                                f"{q.get('answer')} 不符"
                            )
            elif verify is not None and not isinstance(verify, str):
                errors.append(f"questions[{i}]（{qid}）verify 须为字符串")

    for i, d in enumerate(deps):
        if not isinstance(d, dict):
            errors.append(f"dependencies[{i}] 不是对象")
            continue
        if d.get("from") not in topic_ids:
            errors.append(f"dependencies[{i}] from 不存在：{d.get('from')}")
        if d.get("to") not in topic_ids:
            errors.append(f"dependencies[{i}] to 不存在：{d.get('to')}")
        if d.get("from") == d.get("to"):
            errors.append(f"dependencies[{i}] 自指：{d.get('from')}")

    if warnings:
        print(f"WARNING（{len(warnings)} 项）：")
        for w in warnings[:30]:
            print(" -", w)
    if errors:
        print(f"VALIDATION FAILED（{len(errors)} 项）：")
        for e in errors[:30]:
            print(" -", e)
        return 1
    print(
        f"VALIDATION PASSED（知识点 {len(topics)} 条，"
        f"题目 {len(questions)} 道，先修边 {len(deps)} 条）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
