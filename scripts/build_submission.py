#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汇编 cn-math-taxonomy 沪教版小学数学映射成品包。

骨架：hujiao-math-mapping.md（242 条，旧版目录口径）
覆盖：hujiao-math-g1-mapping.md（42 条，新版）、hujiao-math-g23-mapping.md（90 条，新版）
校验依据：项目 topics.json、新版目录原文两份。

合并细则（与任务书规则 1 的对应关系，及两处需要说明的解释）：
- 两份新版表出现过的条目以新版判定覆盖旧版，basis=new；
  两表都有的条目按底稿自身的回填/主落点指向定夺（见 G1_PRIMARY 与回填说明）。
- g23「无对应」表的判定范围是新版二上/二下/三上：旧落点在此范围内的条目
  改判 none（basis=new）；旧落点在四/五年级的 8 条，新版表未覆盖该范围，
  保留旧版判定（basis=old），仅在备注中注明新版低年级已核查无此内容。
- g23 待补专节 9 条：confidence=pending、status=pending_g3b、basis=old，
  保留旧版落点，待新版三下目录上架后补判。
"""
import json
import random
import re
from pathlib import Path

AUD = Path.home() / "workspace" / "cn-math-taxonomy-audit"
OUT = AUD / "submission"
OUT.mkdir(exist_ok=True)
GEN_DATE = "2026-10-23"

CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6}
CONF = {"明确": "exact", "大致": "approx", "无": "none"}


# ---------------------------------------------------------------- 解析工具

def region_lines(text, start_marker):
    """取 start_marker 所在行之后、下一个以 # 开头的行之前的行。"""
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if start_marker in ln:
            start = i + 1
            break
    if start is None:
        raise ValueError(f"region not found: {start_marker}")
    out = []
    for ln in lines[start:]:
        if ln.startswith("#"):
            break
        out.append(ln)
    return out


def table_rows(lines):
    rows = []
    for ln in lines:
        ln = ln.strip()
        if ln.startswith("| cnm_p"):
            cells = [c.strip() for c in ln.strip("|").split("|")]
            rows.append(cells)
    return rows


def parse_volume(s):
    s = (s or "").strip()
    if s in ("—", "-", ""):
        return None
    m = re.match(r"([一二三四五六])年级(上|下)册", s)
    if not m:
        raise ValueError(f"bad volume: {s}")
    return CN[m.group(1)], m.group(2)


def split_unit_section(cell):
    """把 '单元（小节）' 拆为 (unit, section)；取第一个其配平括号恰好收尾的括号组为小节。"""
    cell = (cell or "").strip()
    i = 0
    while i < len(cell):
        if cell[i] == "（":
            depth, j = 0, i
            while j < len(cell):
                if cell[j] == "（":
                    depth += 1
                elif cell[j] == "）":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            if j == len(cell) - 1:
                return cell[:i].strip(), cell[i + 1:j].strip()
            i = j + 1
        else:
            i += 1
    return cell, None


def conf_of(cell):
    cell = cell.strip()
    for k, v in CONF.items():
        if cell.startswith(k):
            return v
    raise ValueError(f"bad confidence: {cell}")


def clean_name(cell):
    return re.sub(r"（[一二三四五六][上下]）\s*$", "", cell.strip()).strip()


# ---------------------------------------------------------------- 读底稿

base_text = (AUD / "hujiao-math-mapping.md").read_text(encoding="utf-8")
g1_text = (AUD / "hujiao-math-g1-mapping.md").read_text(encoding="utf-8")
g23_text = (AUD / "hujiao-math-g23-mapping.md").read_text(encoding="utf-8")

topics = json.loads(
    (Path.home() / "workspace" / "cn-math-taxonomy" / "data" / "topics.json").read_text(encoding="utf-8")
)
topic_info = {t["id"]: t for t in topics if t["id"].startswith("cnm_p")}
assert len(topic_info) == 242, len(topic_info)

# 骨架：旧版全量表（主对照表区）
base = {}
for cells in table_rows(region_lines(base_text, "## 对照表（按项目知识点）")):
    tid, name, vol, unit_cell, conf, note = cells
    base[tid] = {
        "name_draft": clean_name(name),
        "vol": parse_volume(vol),
        "unit_cell": unit_cell,
        "conf": conf_of(conf),
        "note": note,
    }
assert len(base) == 242, len(base)

# 一年级新版表（两册）
g1 = {}
for sec in ("### 一年级上册（新版）", "### 一年级下册（新版）"):
    for cells in table_rows(region_lines(g1_text, sec)):
        tid, name, vol, unit_cell, conf, note = cells
        g1[tid] = {
            "vol": parse_volume(vol),
            "unit_cell": unit_cell,
            "conf": conf_of(conf),
            "note": note,
        }
assert len(g1) == 42, len(g1)

# 二三上新版表（主表三册 + 跨表 + 无对应 + 待补）
g23_main = {}
for sec, vol in (
    ("### 二年级上册（新版）", (2, "上")),
    ("### 二年级下册（新版）", (2, "下")),
    ("### 三年级上册（新版）", (3, "上")),
):
    for cells in table_rows(region_lines(g23_text, sec)):
        tid, name, unit_cell, conf, note = cells
        g23_main[tid] = {"vol": vol, "unit_cell": unit_cell, "conf": conf_of(conf), "note": note}

g23_cross = {}
for cells in table_rows(region_lines(g23_text, "### 落点在一年级（跨表解决")):
    tid, name, landing, conf, note = cells
    g23_cross[tid] = {"landing": landing, "conf": conf_of(conf), "note": note}

g23_none = {}
for cells in table_rows(region_lines(g23_text, "### 无对应（新版二上/二下/三上范围内）")):
    tid, name, note = cells
    g23_none[tid] = {"note": note}

g23_pending = {}
for cells in table_rows(region_lines(g23_text, "## 三年级下册待补判")):
    tid, name, old_judgment, todo = cells
    g23_pending[tid] = {"old_judgment": old_judgment, "todo": todo}

g23_ids = set(g23_main) | set(g23_cross) | set(g23_none) | set(g23_pending)
assert len(g23_main) == 56, len(g23_main)
assert len(g23_none) == 24, len(g23_none)
assert len(g23_pending) == 9, len(g23_pending)
assert len(g23_ids) == 90, len(g23_ids)


# ---------------------------------------------------------------- 合并

# g23 无对应表中、旧落点在四/五年级（新版表未覆盖范围）的条目：保留旧版判定
KEEP_OLD_OUT_OF_SCOPE = {
    "cnm_p063", "cnm_p070", "cnm_p076", "cnm_p080",
    "cnm_p093", "cnm_p094", "cnm_p099", "cnm_p227",
}
# 两份新版表都出现、且主落点在一年级表的条目（g23 中为再现/跨表登记，不覆盖）
G1_PRIMARY = {"cnm_p040", "cnm_p045", "cnm_p060"}


def make_record(tid, vol, unit_cell, conf, basis, status, note):
    t = topic_info[tid]
    if vol is None or conf == "none":
        hg, hs, unit, section = None, None, None, None
    else:
        hg, hs = vol
        unit, section = split_unit_section(unit_cell)
    return {
        "topic_id": tid,
        "topic_name": t["name"],
        "renjiao_grade": t["grade"],
        "renjiao_semester": t["semester"],
        "hujiao_grade": hg,
        "hujiao_semester": hs,
        "hujiao_unit": unit,
        "hujiao_section": section,
        "confidence": conf,
        "basis": basis,
        "status": status,
        "notes": note,
    }
records = {}

# 1) 骨架：旧版判定
for tid, r in base.items():
    records[tid] = make_record(tid, r["vol"], r["unit_cell"], r["conf"], "old", "judged", r["note"])

# 2) 三下待补（保留旧版落点，改状态与置信度）
for tid, p in g23_pending.items():
    rec = records[tid]
    rec["confidence"] = "pending"
    rec["status"] = "pending_g3b"
    extra = f"【三下待补】{p['todo']}；新版三下目录平台未上架（2026-10-23 核查），保留旧版判定（{p['old_judgment']}）待补判。"
    rec["notes"] = (rec["notes"] + "；" if rec["notes"] else "") + extra

# 3) 一年级新版覆盖
for tid, r in g1.items():
    records[tid] = make_record(tid, r["vol"], r["unit_cell"], r["conf"], "new", "judged", r["note"])

# 4) 二三上新版主表覆盖（G1_PRIMARY 除外：p040/p060 在 g23 为再现落点、p045 为跨表登记）
for tid, r in g23_main.items():
    if tid in G1_PRIMARY:
        rec = records[tid]
        add = {
            "cnm_p040": "新版三上第6单元周长（长度的测量）为再现落点。",
            "cnm_p060": "新版二上第6单元数学广场（找规律）为再现落点。",
        }[tid]
        rec["notes"] = (rec["notes"] + "；" if rec["notes"] else "") + add
        continue
    records[tid] = make_record(tid, r["vol"], r["unit_cell"], r["conf"], "new", "judged", r["note"])
for tid, r in g23_cross.items():  # cnm_p045：与一年级表一致，仅补注
    rec = records[tid]
    add = "二、三年级上册新版无再现落点（二三上对照表跨表登记确认）。"
    rec["notes"] = (rec["notes"] + "；" if rec["notes"] else "") + add

# 一年级表中被二三上回填的条目（p015/p032/p034/p036/p217）已由步骤 4 的二上判定覆盖；
# p037 的二上判定取自 g23 主表，再补一年级活动一句：
records["cnm_p037"]["notes"] += "；一年级新版第1、2单元活动亦有分类渗透（见一年级对照表），但正式落点为二上专单元。"

# 5) 二三上新版「无对应」表
for tid, r in g23_none.items():
    if tid in KEEP_OLD_OUT_OF_SCOPE:
        rec = records[tid]
        add = "新版二上/二下/三上目录已核查无此内容；旧版落点在四/五年级，不在新版已收集范围内，保留旧版判定。"
        rec["notes"] = (rec["notes"] + "；" if rec["notes"] else "") + add
    else:
        records[tid] = make_record(tid, None, None, "none", "new", "judged", r["note"])


# ---------------------------------------------------------------- 校验

ids = list(records)
assert len(ids) == 242 and len(set(ids)) == 242
assert set(ids) == set(topic_info) == set(base)

# 名称一致性（底稿名 vs topics.json 名）
name_mismatch = [
    tid for tid in ids if base[tid]["name_draft"] != topic_info[tid]["name"]
]

# 新版表覆盖关系：两份新版表条目必须全部进入成品且口径一致
assert set(g1) <= set(records) and g23_ids <= set(records)
for tid in g1:
    assert records[tid]["basis"] == "new", tid
for tid in g23_main:
    assert records[tid]["basis"] == "new", tid
for tid in g23_none:
    expect = "old" if tid in KEEP_OLD_OUT_OF_SCOPE else "new"
    assert records[tid]["basis"] == expect, tid
for tid in g23_pending:
    assert records[tid]["status"] == "pending_g3b" and records[tid]["confidence"] == "pending", tid

# 判定一致性抽核（关键回填/双表条目）
spot_expected = {
    "cnm_p036": ("new", "exact", 2, "上"),
    "cnm_p032": ("new", "exact", 2, "上"),
    "cnm_p034": ("new", "approx", 2, "上"),
    "cnm_p015": ("new", "approx", 2, "上"),
    "cnm_p217": ("new", "approx", 2, "上"),
    "cnm_p045": ("new", "exact", 1, "下"),
    "cnm_p040": ("new", "approx", 1, "下"),
    "cnm_p060": ("new", "approx", 1, "下"),
    "cnm_p063": ("old", "approx", 5, "上"),
    "cnm_p088": ("old", "pending", 3, "上"),
    "cnm_p108": ("new", "none", None, None),
    "cnm_p056": ("new", "none", None, None),
}
for tid, (b, c, g, s) in spot_expected.items():
    r = records[tid]
    assert (r["basis"], r["confidence"], r["hujiao_grade"], r["hujiao_semester"]) == (b, c, g, s), (tid, r)

from collections import Counter

conf_dist = Counter(r["confidence"] for r in records.values())
basis_dist = Counter(r["basis"] for r in records.values())
status_dist = Counter(r["status"] for r in records.values())

# 随机抽 15 条（固定种子），标注其判定来源，供回底稿原文人工核对
random.seed(20261023)
sample_ids = random.sample(sorted(ids), 15)
sample_report = []
for tid in sample_ids:
    r = records[tid]
    if r["status"] == "pending_g3b":
        src = "待补专节+旧版底稿"
    elif tid in g23_main and tid not in G1_PRIMARY:
        src = "二三上新版表"
    elif tid in g23_none and tid not in KEEP_OLD_OUT_OF_SCOPE:
        src = "二三上新版表（无对应）"
    elif tid in g1:
        src = "一年级新版表"
    else:
        src = "旧版底稿"
    sample_report.append(
        {
            "topic_id": tid,
            "topic_name": r["topic_name"],
            "source": src,
            "confidence": r["confidence"],
            "basis": r["basis"],
            "hujiao": (
                f"{r['hujiao_grade']}年级{r['hujiao_semester']}册 {r['hujiao_unit']}"
                if r["hujiao_grade"]
                else "—"
            ),
        }
    )
# ---------------------------------------------------------------- 反向缺口（三份底稿合并去重）
# basis: new=新版目录确认；old=旧版目录；new+old=两版目录均有
REVERSE_GAPS = [
    # —— 时间类（结构性缺口：项目无任何「认识钟表/整时/半时/读出时刻」知识点）——
    {"content": "时间的初步认识：整时、半时", "location": "新版一下 第3单元", "basis": "new", "project_status": "无", "note": "项目一年级无任何时间类知识点，全项目亦无「认识钟表」条目；最近的条目为二下 cnm_p061 秒的认识、cnm_p062 时、分、秒的进率"},
    {"content": "制作钟面、读出钟面上的时刻", "location": "新版二下 第3单元 时间在哪里", "basis": "new", "project_status": "无", "note": "二下时间单元 4 节中仅「感受分和秒」被 cnm_p061/cnm_p062 覆盖，钟面认读本体缺失；时间类缺口自一年级延续至二年级"},
    {"content": "合理安排时间", "location": "新版二下 第3单元 时间在哪里", "basis": "new", "project_status": "无", "note": "时间规划，与 cnm_p063 经过时间（时长计算）口径不同"},
    {"content": "计时工具的发展", "location": "新版二下 第3单元 智慧小站", "basis": "new", "project_status": "无", "note": "文化阅读类，可不单设知识点，仅记录"},
    {"content": "制订作息时间表", "location": "新版三上 第5单元 年、月、日的秘密", "basis": "new", "project_status": "无", "note": "年、月、日的应用；与 cnm_p092 24时记时法弱相关（是否含 24 时记时法待课时确认）"},
    # —— 新版目录确认的缺口 ——
    {"content": "数墙的秘密（数墙）", "location": "新版一下 第7单元 数学广场；旧版一上 三、五单元", "basis": "new+old", "project_status": "无", "note": "计算推理类"},
    {"content": "组算式", "location": "新版一下 第1单元；旧版一上 五、整理与提高", "basis": "new+old", "project_status": "无", "note": "由一组数写加减算式"},
    {"content": "大家来做加法", "location": "新版一上 第6单元；旧版一上 五、整理与提高", "basis": "new+old", "project_status": "无", "note": "加法表的整理，项目无此知识点"},
    {"content": "大家来做减法", "location": "新版一下 第1单元；旧版一上 五、整理与提高", "basis": "new+old", "project_status": "无", "note": "减法表的整理，同上"},
    {"content": "加与减（加减互逆的直观认识，一年级口径）", "location": "新版一上 第4单元", "basis": "new", "project_status": "无", "note": "项目 cnm_p220 加减法各部分间的关系（二下）为正式关系表述，口径不同"},
    {"content": "长度的比较（长短、高矮比较）", "location": "新版一下 第5单元", "basis": "new", "project_status": "无", "note": "cnm_p040 仅覆盖「测量」部分"},
    {"content": "布置教室——挂彩旗", "location": "新版一下 第6单元 身体上的尺子", "basis": "new", "project_status": "无", "note": "综合实践：用身体上的尺子做测量与布置"},
    {"content": "玩一玩、认一认（入学活动）", "location": "新版一上 第1单元 我是小学生", "basis": "new", "project_status": "无", "note": "同单元「说一说」与 cnm_p022 弱相关"},
    {"content": "20以内数的排列（数序）", "location": "新版一上 第5单元", "basis": "new", "project_status": "弱", "note": "cnm_p016 覆盖 11~20 的认读写与组成，无「数的排列/数序」专条"},
    {"content": "数的位置", "location": "新版一下 第2单元", "basis": "new", "project_status": "弱", "note": "cnm_p028、cnm_p029 部分相关，无专条（是否含数射线待课时确认）"},
    {"content": "相邻的数", "location": "新版一下 第2单元；二下 第2单元亦有", "basis": "new", "project_status": "弱", "note": "cnm_p028 部分相关，无专条"},
    {"content": "幻方", "location": "新版二上 第6单元 数学广场；旧版二上 六、整理与提高", "basis": "new+old", "project_status": "无", "note": ""},
    {"content": "数位表上的游戏（旧版称位值图上的游戏）", "location": "新版二下 第2单元 万以内的数；旧版二下 二、千以内数的认识与表达", "basis": "new+old", "project_status": "无", "note": "旧版目录转载有「位置图上的游戏」异文，按术语体系应为位值图"},
    {"content": "一起来购物（付钱、找零、比价）", "location": "新版二上 第2单元 欢乐购物街", "basis": "new", "project_status": "弱", "note": "cnm_p036 仅覆盖「认识人民币」"},
    {"content": "我的学校（描述学校位置）", "location": "新版二上 第4单元 我的学校我的家", "basis": "new", "project_status": "弱", "note": "cnm_p049 方位、cnm_p181 路线描述部分相关，无专条"},
    {"content": "玩转“24点”", "location": "新版二下 第1单元 数学好玩栏目", "basis": "new", "project_status": "无", "note": ""},
    {"content": "七巧板", "location": "新版三上 第8单元 数学广场", "basis": "new", "project_status": "无", "note": "拼图活动；项目 cnm_p024 平面图形的拼组为一年级口径，仅弱相关"},
    {"content": "上海半程马拉松的路线设计", "location": "新版三上 第7单元 马拉松的路线设计", "basis": "new", "project_status": "无", "note": "千米的综合实践，项目无对应综合实践条目"},
    # —— 旧版目录的缺口（新版对应册目录未收集或未见专节）——
    {"content": "数射线（及看数射线做加、减法、数射线（千））", "location": "旧版一上起，贯穿低年级", "basis": "old", "project_status": "无", "note": "人教体系用直尺/线段图替代，项目未设点；新版一至三上目录亦未见「数射线」专节名，其在新版低年级的存废待课时确认"},
    {"content": "加倍与一半", "location": "旧版一上 五、整理与提高", "basis": "old", "project_status": "无", "note": "新版一年级目录未见"},
    {"content": "推算", "location": "旧版一上 五、整理与提高", "basis": "old", "project_status": "无", "note": "计算推理类，项目仅有「简单的变化规律」弱对应"},
    {"content": "各人眼中的20", "location": "旧版一下 六、整理与提高", "basis": "old", "project_status": "无", "note": "新版一年级目录未见"},
    {"content": "方框里填几（方框算式/未知数启蒙）", "location": "旧版二上 一、复习与提高", "basis": "old", "project_status": "无", "note": "无独立知识点"},
    {"content": "巧算系列（巧算、巧算（2）、看谁算得巧）", "location": "旧版二上、二下、四下", "basis": "old", "project_status": "无", "note": "项目只有「用运算律简便计算」，无沪教版式巧算专题"},
    {"content": "点图与数", "location": "旧版二上 六、整理与提高（数学广场）", "basis": "old", "project_status": "无", "note": ""},
    {"content": "列表枚举", "location": "旧版二下 七、整理与提高（数学广场）", "basis": "old", "project_status": "无", "note": "项目搭配类仅「简单的搭配」"},
    {"content": "流程图（1）、流程图（2）", "location": "旧版二下、三上（数学广场）", "basis": "old", "project_status": "无", "note": ""},
    {"content": "多连块（正方形组成的图形）", "location": "旧版三上 一、复习与提高", "basis": "old", "project_status": "无", "note": ""},
    {"content": "树叶的面积、不规则图形面积估测", "location": "旧版三下 一、复习与提高；五下另有「面积的估测」", "basis": "old", "project_status": "无", "note": "项目只有规则图形面积与组合图形面积"},
    {"content": "计算器单元（从算筹到计算器、算盘、使用计算器计算）", "location": "旧版三下 四、计算器", "basis": "old", "project_status": "无", "note": "项目仅在个别知识点中使用计算器，无独立知识点"},
    {"content": "树状算图、正推、逆推、文字计算题", "location": "旧版四上 四、整数的四则运算", "basis": "old", "project_status": "无", "note": ""},
    {"content": "分数墙（小研究——“分数墙”）", "location": "旧版四上 三、分数的初步认识（二）", "basis": "old", "project_status": "无", "note": ""},
    {"content": "五舍六入", "location": "旧版四下 五、整理与提高（数学广场）", "basis": "old", "project_status": "无", "note": "项目近似数只有四舍五入"},
    {"content": "计算比赛场次", "location": "旧版四下 五、整理与提高（数学广场）", "basis": "old", "project_status": "无", "note": ""},
    {"content": "可能情况的个数", "location": "旧版五下 五、问题解决", "basis": "old", "project_status": "弱", "note": "项目有「可能性」「可能性的大小」，无计数口径的「可能情况的个数」"},
    {"content": "表面积的变化、体积与重量", "location": "旧版五下 五、问题解决", "basis": "old", "project_status": "无", "note": ""},
    {"content": "行程（行程问题专题）", "location": "旧版五下 五、问题解决", "basis": "old", "project_status": "弱", "note": "项目「常见数量关系」未单列行程"},
    {"content": "自然数（概念）", "location": "旧版五下 一、复习与提高", "basis": "old", "project_status": "无", "note": "项目无「自然数」概念知识点"},
    {"content": "循环小数", "location": "旧版五上 二、小数乘除法", "basis": "old", "project_status": "无", "note": "项目小数除法未含循环小数"},
]

# ---------------------------------------------------------------- 输出 JSON

ordered = [records[tid] for tid in sorted(records)]
meta = {
    "title": "cn-math-taxonomy 沪教版（上海）小学数学映射",
    "generated": GEN_DATE,
    "scope": "项目 topics.json 全部 242 个小学数学知识点（cnm_p001–cnm_p242）到沪教版册次/单元/小节的目录级映射",
    "basis说明": {
        "new": "新版目录（2022 年版课程标准修订，上海教育出版社，国家中小学智慧教育平台电子教材抄录）：一年级上/下、二年级上/下、三年级上共 5 册",
        "old": "旧版目录（二期课改试用本，上海教育出版社）：四、五年级现行在用版本；一至三年级未被新版覆盖的条目亦暂用旧版判定",
    },
    "字段说明": {
        "confidence": "exact=有名称相同或内容对应的小节；approx=内容被覆盖但无同名小节/仅部分覆盖/口径不同；none=对应口径目录内无此知识点；pending=待新版三下目录补判",
        "status": "judged=已判定；pending_g3b=待新版三年级下册目录上架后补判（保留旧版落点）",
        "hujiao_grade/semester": "沪教版落点年级（整数）与学期（上/下）；confidence=none 时为 null",
    },
    "stats": {
        "total": len(ordered),
        "confidence": dict(conf_dist),
        "basis": dict(basis_dist),
        "status": dict(status_dist),
        "new_basis_topics": basis_dist.get("new", 0),
        "old_basis_topics": basis_dist.get("old", 0),
        "reverse_gaps": len(REVERSE_GAPS),
    },
    "pending_note": "新版三年级下册目录在国家中小学智慧教育平台暂未上架（2026-10-23 核查），9 条标 pending_g3b；另 cnm_p056（克和千克）、cnm_p108（条形统计图）、cnm_p085（复式统计表）、cnm_p127（轴对称）已判 none（新版二三上无），其实际落点亦待三下目录核查。",
}
doc = {"meta": meta, "mappings": ordered, "reverse_gaps": REVERSE_GAPS}
(OUT / "mappings-hujiao-math.json").write_text(
    json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8"
)

# ---------------------------------------------------------------- 输出对照表 md

VOL_ORDER = [(1, "上"), (1, "下"), (2, "上"), (2, "下"), (3, "上"), (3, "下"),
             (4, "上"), (4, "下"), (5, "上"), (5, "下")]
VOL_NAME = {(1, "上"): "一年级上册", (1, "下"): "一年级下册", (2, "上"): "二年级上册",
            (2, "下"): "二年级下册", (3, "上"): "三年级上册", (3, "下"): "三年级下册",
            (4, "上"): "四年级上册", (4, "下"): "四年级下册", (5, "上"): "五年级上册",
            (5, "下"): "五年级下册"}
CONF_CN = {"exact": "明确", "approx": "大致", "none": "无", "pending": "待补"}
BASIS_CN = {"new": "新版", "old": "旧版"}


def row_md(r):
    sec = r["hujiao_section"] or "—"
    unit = r["hujiao_unit"] or "—"
    return (
        f"| {r['topic_id']} | {r['topic_name']}（{r['renjiao_grade']}{r['renjiao_semester']}） "
        f"| {unit} | {sec} | {CONF_CN[r['confidence']]} | {BASIS_CN[r['basis']]} | {r['notes']} |"
    )


lines = [
    "# 沪教版小学数学映射对照表（提交版）",
    "",
    f"共 {len(ordered)} 条。置信度分布：明确 {conf_dist.get('exact', 0)}、大致 {conf_dist.get('approx', 0)}、"
    f"无对应 {conf_dist.get('none', 0)}、待补 {conf_dist.get('pending', 0)}。"
    f"口径：新版目录 {basis_dist.get('new', 0)} 条、旧版目录 {basis_dist.get('old', 0)} 条。",
    "排序：按沪教版年级学期；同册内按单元、ID。无对应与待补（三下）单列于文末。",
    "",
]
judged = [r for r in ordered if r["confidence"] in ("exact", "approx")]
for vol in VOL_ORDER:
    grp = [r for r in judged if (r["hujiao_grade"], r["hujiao_semester"]) == vol]
    if not grp:
        continue
    grp.sort(key=lambda r: (r["hujiao_unit"] or "", r["topic_id"]))
    lines += [f"## {VOL_NAME[vol]}（{len(grp)} 条）", "",
              "| 项目ID | 项目知识点（人教口径） | 沪教版单元 | 小节 | 置信度 | 口径 | 备注 |",
              "|---|---|---|---|---|---|---|"]
    lines += [row_md(r) for r in grp]
    lines.append("")
none_grp = [r for r in ordered if r["confidence"] == "none"]
lines += [f"## 无对应（{len(none_grp)} 条）", "",
          "| 项目ID | 项目知识点（人教口径） | 沪教版单元 | 小节 | 置信度 | 口径 | 备注 |",
          "|---|---|---|---|---|---|---|"]
lines += [row_md(r) for r in none_grp]
lines.append("")
pend_grp = [r for r in ordered if r["status"] == "pending_g3b"]
lines += [f"## 待补：新版三年级下册目录未上架（{len(pend_grp)} 条，暂按旧版落点列示）", "",
          "| 项目ID | 项目知识点（人教口径） | 沪教版单元（旧版） | 小节（旧版） | 置信度 | 口径 | 备注 |",
          "|---|---|---|---|---|---|---|"]
lines += [row_md(r) for r in pend_grp]
lines.append("")
(OUT / "mapping-table.md").write_text("\n".join(lines), encoding="utf-8")

# ---------------------------------------------------------------- 输出 README

gap_lines = []
for i, g in enumerate(REVERSE_GAPS, 1):
    gap_lines.append(
        f"| {i} | {g['content']} | {g['location']} | {g['basis']} | {g['project_status']} | {g['note']} |"
    )

readme = f"""# 沪教版（上海）小学数学映射 — 提交说明

本包是 cn-math-taxonomy 项目 242 个小学数学知识点（topics.json 中 cnm_p001–cnm_p242）到
**沪教版**册次 / 单元 / 小节的映射数据，供项目增加「教材版本映射」层时直接取用
（对应 Issue #11 的提议）。生成日期：{GEN_DATE}。

## 文件

| 文件 | 内容 |
|---|---|
| `mappings-hujiao-math.json` | 机器可读成品：顶层 meta（口径、统计）+ mappings 记录数组（242 条）+ reverse_gaps（反向缺口） |
| `mapping-table.md` | 人读对照表：按沪教版年级学期排序，无对应与待补单列分区 |

## 背景与用途

- 项目现按人教版（六三制）编排；上海使用沪教版、五四制：小学数学为上海教育出版社
  沪教版，年级与册次顺序与人教版差异较大（本次映射中有对应条目近三成跨年级/跨册）。
- 本映射只做一层「版本对照」：不改动项目知识点本身，只给出每个知识点在沪教版中的
  落点（年级、学期、单元、小节）与置信度，站点可据此按沪教版顺序呈现与筛选。
- 同一机制可复用于其他地方版本（苏教版、北师大版等）。

## 数据来源

- **新版目录（2022 年版课程标准修订）**：国家中小学智慧教育平台（basic.smartedu.cn）
  电子教材逐页抄录，共 5 册：一年级上册、一年级下册、二年级上册、二年级下册、
  三年级上册。均为上海教育出版社，主编李大潜。已知 ISBN：
  一年级上册 978-7-5720-2757-4（定价 6.50 元，国家教材委员会专家委员会 2024 年审核通过）；
  一年级下册 978-7-5720-3241-7（定价 6.45 元，2024 年审核通过）。
  二、三年级 3 册的电子书版权页被截断、封底条码区被遮挡，ISBN 在平台上不可见
  （二年级下册定价 6.80 元可读），故未列。
- **旧版目录（二期课改试用本）**：《九年义务教育课本·数学（试用本）》，上海教育出版社，
  共 10 册；目录文本取自两处独立转载并互相核对、另与教师教学计划交叉核对。
  该版是 2026 年秋四、五年级实际在用版本；四、五年级映射以此为准。一至三年级
  未被新版目录覆盖的少数条目亦暂用旧版判定（逐条在 basis 字段标明）。
- **三年级下册（新版）**：2026-10-23 核查时平台尚未上架，无从抄录（详见「待补项」）。

## 合并口径

- 以旧版全量对照（242 条）为骨架；凡新版目录已覆盖的条目（一至三上），一律以
  新版判定覆盖旧版判定，字段 `basis` 标 `new`；其余保留旧版判定，`basis` 标 `old`。
- 两份新版底稿的交叉条目按底稿自身的回填结论定夺：一年级判「无对应」的
  人民币、100 以内减法、分类与整理、求两数相差几、上下前后左右 6 条，已在
  二年级上册新版目录中确认落点，成品取二上落点；反之主落点在一年级的
  认识厘米、用身体上的长度估测、简单的变化规律 3 条取一年级落点，
  二/三上同名小节只作再现注记。
- 新版「无对应」的判定范围是新版二上/二下/三上：旧落点在此范围内的条目改判
  none；旧落点在四、五年级的 8 条（经过时间、吨的认识、数字编码、同分母分数的
  初步加减、一位小数的初步认识、一位小数的加减、线段直线和射线、简单的分数
  大小比较），新版目录未覆盖该范围，保留旧版判定并在备注中注明低年级已核查无。
- 本映射为**目录级映射**（单元/小节名对应），未逐课核对课时内容；「大致」条目
  仍是后续精修的对象。

## 字段说明（mappings 每条记录）

| 字段 | 含义 |
|---|---|
| topic_id / topic_name | 项目知识点 ID 与名称（与 topics.json 一致，已逐条核对） |
| renjiao_grade / renjiao_semester | 项目口径（人教版）年级（整数）与学期（上/下） |
| hujiao_grade / hujiao_semester | 沪教版落点年级（整数）与学期（上/下）；无对应时为 null |
| hujiao_unit / hujiao_section | 沪教版单元名与小节名；小节为 null 表示只定位到单元 |
| confidence | exact 明确（有名称相同或内容对应的小节）/ approx 大致（内容被覆盖但无同名小节、仅部分覆盖或口径不同）/ none 无对应 / pending 待补判 |
| basis | new 新版目录（2022 课标）/ old 旧版目录（二期课改试用本） |
| status | judged 已判定 / pending_g3b 待新版三下目录补判 |
| notes | 判定说明、与旧版的差异、待课时确认事项等 |

## 覆盖统计

- 总条数 **{len(ordered)}**（唯一 topic_id {len(set(ids))}）。
- 置信度：明确 exact {conf_dist.get('exact', 0)} 条、大致 approx {conf_dist.get('approx', 0)} 条、
  无对应 none {conf_dist.get('none', 0)} 条、待补 pending {conf_dist.get('pending', 0)} 条。
- 口径：新版目录 new {basis_dist.get('new', 0)} 条、旧版目录 old {basis_dist.get('old', 0)} 条
  （old 中含待补 {status_dist.get('pending_g3b', 0)} 条）。
- 反向缺口（沪教版有、项目无对应知识点）共 **{len(REVERSE_GAPS)}** 项（见下表与 JSON 的 reverse_gaps）。

## 反向缺口汇总（沪教版有、项目无/明显偏弱）

basis 列：new=新版目录；old=旧版目录；new+old=两版均有。

| # | 沪教版内容 | 所在册次 | 口径 | 项目现状 | 说明 |
|---|---|---|---|---|---|
{chr(10).join(gap_lines)}

最值得优先补的是**时间类**：项目没有任何「认识钟表 / 整时 / 半时 / 读出时刻」
知识点，而沪教版新版在一年级下册设「时间的初步认识」（整时、半时）、二年级下册
设「时间在哪里」（制作钟面、读出钟面上的时刻、感受分和秒）——目前只有
「感受分和秒」能被项目的 cnm_p061/cnm_p062 覆盖，钟面认读本体在一年级、二年级
两个学段连续缺失。其余沪教特色内容如数射线、数墙、幻方、巧算、树状算图等
项目亦未设点，如需完整适配上海课程，可按上表新增知识点。

## 待补项

1. **新版三年级下册目录未上架**：以下 {len(pend_grp)} 条暂保留旧版落点、标 pending_g3b，
   待目录到位后补判：
   {('、'.join(r['topic_id'] + ' ' + r['topic_name'] for r in pend_grp))}。
   其中 cnm_p088 面积的意义、cnm_p089 长方形和正方形的面积的旧版落点（三上几何小实践）
   在新版三上已失效（新版三上只有周长、无面积），大概率移至三下。
2. 另需随三下目录一并核查实际落点的已判条目：cnm_p056 克和千克（新版二下质量单元
   整体消失）、cnm_p108 条形统计图与 cnm_p085 复式统计表（新版二三上无任何统计内容）、
   cnm_p127 轴对称（新版三上未见）——四条目前按新版二三上判 none。
3. 待课时内容确认（目录级映射的固有限制）：新版一年级「数的位置」是否含数射线、
   cnm_p015 上下前后左右在二上「我的房间」中的实际内容、cnm_p058 两步四则运算是否
   含小括号、cnm_p067 毫米是否在三上「长度的测量」内、cnm_p092 三上「制订作息时间表」
   是否含 24 时记时法、cnm_p122 三上初步认识是否含三角形分类。
4. 旧版目录小异文：二下「位值图上的游戏」目录转载作「位置图上的游戏」，按术语
   体系应为位值图，待纸质书核对；旧版四上未单列「公顷」，cnm_p098 暂判 approx。

## 使用建议

- 接入时建议把 mappings 作为独立数据文件挂接（以 topic_id 为键），不要改写
  项目原 topics.json 的年级/章节字段；basis 与 confidence 应一并呈现给使用者，
  以便区分新版/旧版口径与判定强度。
- pending_g3b 条目在三下目录补判前，建议在沪教版视图中单列或加注，不要按旧版
  落点直接呈现给三年级下册使用者。
- 反向缺口如后续新增知识点，ID 建议沿用 cnm_p 序列续编，并回填本映射。
"""
(OUT / "README.md").write_text(readme, encoding="utf-8")

# ---------------------------------------------------------------- 汇总打印

print("== 汇编完成 ==")
print(f"总条数: {len(ordered)}（唯一 ID {len(set(ids))}）")
print(f"confidence 分布: {dict(conf_dist)}")
print(f"basis 分布: {dict(basis_dist)}（新版 {basis_dist.get('new', 0)} / 旧版 {basis_dist.get('old', 0)}）")
print(f"status 分布: {dict(status_dist)}")
print(f"反向缺口: {len(REVERSE_GAPS)} 项")
print(f"名称不一致（底稿 vs topics.json）: {name_mismatch if name_mismatch else '无'}")
print("== 随机抽查 15 条（固定种子 20261023）==")
for s in sample_report:
    print(f"  {s['topic_id']} {s['topic_name']} | 来源:{s['source']} | {s['confidence']}/{s['basis']} | {s['hujiao']}")
