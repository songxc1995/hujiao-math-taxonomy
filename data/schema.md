# 数据字段说明

## topics.json：知识点（数组）

| 字段 | 说明 |
|------|------|
| id | 知识点编号，格式 `hjm_g{年级}{学期}{u单元号}_l{小节号}`，如 `hjm_g1a_u3_l1`（a=上册，b=下册） |
| name | 小节名称（来自教材目录） |
| grade | 年级（数字） |
| term | 学期：`上` / `下` |
| unit | 单元名称 |
| unit_no | 单元序号（数字） |
| page | 小节起始页码（教材印刷页） |
| kind | 类型：`概念` / `技能` / `活动` / `应用`（暂定，后续可调） |
| description | 知识点描述（待原创填写，现为空） |
| mastery | 掌握标准（字符串数组，待原创填写，现为空） |

说明：目录中的「小练习」「复习」是练习环节，不是知识点，不建条目。

## questions.json：题目（数组，现为空）

| 字段 | 说明 |
|------|------|
| id | 题目编号，格式 `{知识点id}_q{序号}` |
| topicId | 所属知识点 id，必须存在于 topics.json |
| difficulty | 难度：`basic` / `medium` / `hard` |
| type | 题型：`numeric`（填数）/ `choice`（选择）/ `text`（文字作答） |
| prompt | 题面（必须原创） |
| answer | 答案 |
| explanation | 讲解（必须原创） |
| verify | 可选：答案机算验证表达式，如 `3+1` |

## dependencies.json：先修关系（数组，现为空）

每条为 `{"from": "先修知识点id", "to": "后续知识点id"}`，两端 id 必须存在于 topics.json，且不能自指。
