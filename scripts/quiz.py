#!/usr/bin/env python3
"""摸底小工具（命令行版，仅标准库）。

用法：
    python3 scripts/quiz.py [--data-dir DATA_DIR] list [--grade N] [--term 上|下] [--subject 数学|英语]
    python3 scripts/quiz.py [--data-dir DATA_DIR] ask [--topic ID] [--unit 单元名]
                            [--grade N] [--term 上|下] [--subject 数学|英语] [--count N] [--seed N]

默认数据目录为脚本所在目录的 ../data/；--data-dir 可指定其他目录。
答题进度累计保存在运行目录（当前工作目录）下的 quiz-progress.json。

判分规则（归一化后比对：全半角统一、去全部空白、英文字母不分大小写）：
- numeric：归一化后字符串比对；
- choice：接受选项字母（如 A）或选项文本；
- text：归一化后字符串比对。
"""

import argparse
import json
import os
import random
import sys
import unicodedata

PROGRESS_FILE = "quiz-progress.json"


def fail(message):
    print("错误：{}".format(message))
    raise SystemExit(1)


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        fail("无法读取 {}：{}".format(path, e))
    except json.JSONDecodeError as e:
        fail("{} 不是合法 JSON：{}".format(path, e))
    if not isinstance(data, list):
        fail("{} 顶层必须是数组".format(path))
    return data


def resolve_data_dir(explicit):
    if explicit:
        return explicit
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
    )


def load_data(data_dir):
    topics = load_json(os.path.join(data_dir, "topics.json"))
    questions = load_json(os.path.join(data_dir, "questions.json"))
    topic_by_id = {}
    for t in topics:
        if isinstance(t, dict) and t.get("id"):
            topic_by_id[t["id"]] = t
    usable = []
    for q in questions:
        if not isinstance(q, dict):
            continue
        if q.get("topicId") not in topic_by_id:
            print("提示：题目 {} 的知识点不存在，已跳过。".format(q.get("id")))
            continue
        usable.append(q)
    return topics, topic_by_id, usable


def normalize_subject(value):
    """学科归一化：缺字段按数学计；接受中文或英文写法。"""
    if value in (None, "", "数学", "math"):
        return "math"
    if value in ("英语", "english"):
        return "english"
    return str(value)


def filter_topics(topics, grade, term, subject=None):
    result = topics
    if grade is not None:
        result = [t for t in result if t.get("grade") == grade]
    if term is not None:
        result = [t for t in result if t.get("term") == term]
    if subject is not None:
        want = normalize_subject(subject)
        result = [t for t in result if normalize_subject(t.get("subject")) == want]
    return result


def cmd_list(args):
    topics, _topic_by_id, questions = load_data(args.data_dir)
    shown = filter_topics(topics, args.grade, args.term, args.subject)
    counts = {}
    for q in questions:
        counts[q["topicId"]] = counts.get(q["topicId"], 0) + 1
    if not shown:
        print("没有符合条件的知识点。")
        return
    for t in shown:
        n = counts.get(t["id"], 0)
        print("{}  {}（{} · {}年级{}） 题目 {} 道".format(
            t["id"], t["name"], t["unit"], t["grade"], t["term"], n))
    print("共 {} 个知识点。".format(len(shown)))


def normalize_text(value):
    """判分归一化：全半角统一（NFKC）、去全部空白、英文字母不分大小写。"""
    text = unicodedata.normalize("NFKC", str(value))
    return "".join(text.split()).casefold()


def _judge(question, raw):
    """返回是否答对。raw 为用户原始输入。"""
    answer = str(question.get("answer", ""))
    given = raw
    qtype = question.get("type")
    if qtype == "choice":
        options = [str(o) for o in question.get("options", [])]
        picked = None
        if len(given.strip()) == 1 and given.strip().upper().isalpha():
            idx = ord(given.strip().upper()) - ord("A")
            if 0 <= idx < len(options):
                picked = options[idx]
        if picked is None:
            for opt in options:
                if normalize_text(given) == normalize_text(opt):
                    picked = opt
                    break
        if picked is None:
            picked = given
        return normalize_text(picked) == normalize_text(answer)
    return normalize_text(given) == normalize_text(answer)


def cmd_ask(args):
    topics, topic_by_id, questions = load_data(args.data_dir)
    selected = questions
    if args.topic:
        if args.topic not in topic_by_id:
            fail("未找到知识点：{}".format(args.topic))
        selected = [q for q in questions if q["topicId"] == args.topic]
    elif args.unit:
        unit_topics = filter_topics(
            [t for t in topics if t.get("unit") == args.unit], args.grade, args.term,
            args.subject,
        )
        if not unit_topics:
            fail("未找到单元：{}".format(args.unit))
        unit_ids = {t["id"] for t in unit_topics}
        selected = [q for q in questions if q["topicId"] in unit_ids]
    elif args.grade is not None or args.term is not None or args.subject is not None:
        kept = filter_topics(topics, args.grade, args.term, args.subject)
        kept_ids = {t["id"] for t in kept}
        selected = [q for q in questions if q["topicId"] in kept_ids]
    if not selected:
        print("没有找到题目（题库可能为空，或所选范围暂无题目）。")
        return
    rng = random.Random(args.seed) if args.seed is not None else random
    rng.shuffle(selected)
    if args.count is not None and args.count > 0:
        selected = selected[: args.count]

    results = []
    try:
        for i, q in enumerate(selected, 1):
            topic = topic_by_id[q["topicId"]]
            print("\n【{}/{}】（{}）{}".format(i, len(selected), topic["name"], q["prompt"]))
            if q.get("type") == "choice":
                for j, opt in enumerate(q.get("options", [])):
                    print("  {}. {}".format(chr(ord("A") + j), opt))
            try:
                raw = input("你的答案：")
            except (EOFError, KeyboardInterrupt):
                print("\n已退出答题（本轮已答题目会正常计入进度）。")
                break
            correct = _judge(q, raw)
            results.append((q["topicId"], correct))
            if correct:
                print("正确")
            else:
                print("错误，答案是：{}".format(q.get("answer")))
                if q.get("explanation"):
                    print("  讲解：{}".format(q["explanation"]))
    except (EOFError, KeyboardInterrupt):
        print("\n已退出答题（本轮已答题目会正常计入进度）。")

    total = len(results)
    correct_count = sum(1 for _tid, ok in results if ok)
    print("\n本轮得分：{}/{}".format(correct_count, total))
    per_topic = {}
    for tid, ok in results:
        stat = per_topic.setdefault(tid, [0, 0])
        stat[1] += 1
        if ok:
            stat[0] += 1
    for tid, (ok, n) in per_topic.items():
        print("  {}：{}/{}".format(topic_by_id[tid]["name"], ok, n))
    if total == 0:
        return
    save_progress(results, topic_by_id)


def save_progress(results, topic_by_id):
    progress = {"total_correct": 0, "total_answered": 0, "by_topic": {}}
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                progress["total_correct"] = int(loaded.get("total_correct", 0))
                progress["total_answered"] = int(loaded.get("total_answered", 0))
                if isinstance(loaded.get("by_topic"), dict):
                    progress["by_topic"] = loaded["by_topic"]
        except (OSError, ValueError):
            print("提示：{} 无法读取，从零开始累计。".format(PROGRESS_FILE))
    for tid, ok in results:
        progress["total_answered"] += 1
        if ok:
            progress["total_correct"] += 1
        entry = progress["by_topic"].setdefault(
            tid, {"name": topic_by_id[tid]["name"], "correct": 0, "answered": 0}
        )
        entry["answered"] += 1
        if ok:
            entry["correct"] += 1
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)
    print("进度已保存到 {}（累计：{}/{}）".format(
        PROGRESS_FILE, progress["total_correct"], progress["total_answered"]))


def main(argv=None):
    parser = argparse.ArgumentParser(description="摸底小工具")
    parser.add_argument("--data-dir", default=None, help="数据目录（默认：脚本所在目录的 ../data/）")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="列出知识点")
    p_list.add_argument("--data-dir", default=argparse.SUPPRESS)
    p_list.add_argument("--grade", type=int, default=None)
    p_list.add_argument("--term", default=None, choices=["上", "下"])
    p_list.add_argument("--subject", default=None, choices=["数学", "英语", "math", "english"])

    p_ask = sub.add_parser("ask", help="出题答题")
    p_ask.add_argument("--data-dir", default=argparse.SUPPRESS)
    p_ask.add_argument("--topic", default=None, help="按知识点 id 出题")
    p_ask.add_argument("--unit", default=None, help="按单元名出题")
    p_ask.add_argument("--grade", type=int, default=None)
    p_ask.add_argument("--term", default=None, choices=["上", "下"])
    p_ask.add_argument("--subject", default=None, choices=["数学", "英语", "math", "english"])
    p_ask.add_argument("--count", type=int, default=None, help="出题数量（默认全部）")
    p_ask.add_argument("--seed", type=int, default=None, help="随机种子（便于复现）")

    args = parser.parse_args(argv)
    args.data_dir = resolve_data_dir(getattr(args, "data_dir", None))
    try:
        if args.command == "list":
            cmd_list(args)
        elif args.command == "ask":
            cmd_ask(args)
    except (EOFError, KeyboardInterrupt):
        print("\n已退出。")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
