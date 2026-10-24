#!/usr/bin/env python3
"""校验 data/topics.json、data/questions.json、data/dependencies.json（仅标准库）。

用法：python3 scripts/validate.py
全部通过时打印 "VALIDATION PASSED" 并以退出码 0 结束，否则打印错误并以退出码 1 结束。
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise SystemExit(f"{name} 顶层必须是数组")
    return data


def main():
    errors = []
    topics = load("topics.json")
    questions = load("questions.json")
    deps = load("dependencies.json")

    topic_ids = set()
    for i, t in enumerate(topics):
        for field in ("id", "name", "grade", "term", "unit", "unit_no", "page", "kind"):
            if field not in t:
                errors.append(f"topics[{i}] 缺字段 {field}")
        tid = t.get("id")
        if tid in topic_ids:
            errors.append(f"topics[{i}] id 重复：{tid}")
        topic_ids.add(tid)
        if t.get("term") not in ("上", "下"):
            errors.append(f"topics[{i}] term 非法：{t.get('term')}")
        if t.get("kind") not in ("概念", "技能", "活动", "应用"):
            errors.append(f"topics[{i}] kind 非法：{t.get('kind')}")

    for i, q in enumerate(questions):
        for field in ("id", "topicId", "difficulty", "type", "prompt", "answer", "explanation"):
            if field not in q:
                errors.append(f"questions[{i}] 缺字段 {field}")
        if q.get("topicId") not in topic_ids:
            errors.append(f"questions[{i}] topicId 不存在：{q.get('topicId')}")
        if q.get("difficulty") not in ("basic", "medium", "hard"):
            errors.append(f"questions[{i}] difficulty 非法：{q.get('difficulty')}")

    for i, d in enumerate(deps):
        if d.get("from") not in topic_ids:
            errors.append(f"dependencies[{i}] from 不存在：{d.get('from')}")
        if d.get("to") not in topic_ids:
            errors.append(f"dependencies[{i}] to 不存在：{d.get('to')}")
        if d.get("from") == d.get("to"):
            errors.append(f"dependencies[{i}] 自指：{d.get('from')}")

    if errors:
        print(f"VALIDATION FAILED（{len(errors)} 项）：")
        for e in errors[:30]:
            print(" -", e)
        return 1
    print(f"VALIDATION PASSED（知识点 {len(topics)} 条，题目 {len(questions)} 道，先修边 {len(deps)} 条）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
