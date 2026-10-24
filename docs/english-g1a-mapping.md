# 牛津上海版（2022 课标新版）一年级上册 英语 → 项目知识点映射

基准目录：`hujiao-english-g1a-new-catalog.md`（2026-10-23 用户实物书目录页转录，权威）。
对照对象：cn-math-taxonomy `data/topics.json` 小学英语全部 208 个知识点（cne_p*，人教版口径，三年级起始）。
判定口径与数学映射一致：**对应**＝项目有内容实质相同的知识点（注明其在项目中的年级）；**相近**＝部分重叠或义项/范围有差；**无**＝项目小学段没有。
关键背景：项目英语从三年级开始，**没有任何一、二年级知识点**——本表所有「对应」都是内容对应、年级错位（沪教一年级的内容，项目放在三至五年级）。

## 逐条映射（22 条）

| # | 沪教新版一上 | 项目对应知识点 | 判定 | 备注 |
|---|---|---|---|---|
| 1 | Starter 准备课（p.2） | cne_p001 英语字母表（三上）为候选 | 待核 | 目录只列页码，内容（疑含字母/课堂用语）需看内页确认 |
| 2 | U1 分时段问候词 morning/afternoon/evening | cne_p005 问候用语（三上，词汇） | 相近 | 项目该点只收 hello/hi/goodbye/thanks，分时段问候词未单列 |
| 3 | U1 问候、告别交际 | cne_p007 问候、告别和致谢（三上，日常表达） | 对应 | |
| 4 | U2 自我介绍 I'm…（介绍名字） | cne_p006 be 动词 am（三上）+ cne_p008 读懂自我介绍（三上） | 对应 | |
| 5 | U2 询问名字 What's your name? | — | 无 | 项目有问年龄/问来自哪里/问是谁，唯独没有问名字 |
| 6 | U2 朋友与欢迎词 friend/welcome/name | cne_p067 描述朋友（四上，词汇） | 相近 | friend 有；welcome、name（名字一词）项目未收 |
| 7 | U3 文具词汇（schoolbag/book/pencil/ruler/eraser/pencil case） | cne_p063 书包里的文具（三下，词汇） | 对应 | pencil case 项目未收；book 在 cne_p044（三下） |
| 8 | U3 谈论书包里有什么 | cne_p064 谈论书包里有什么（三下）+ cne_p065 读懂书包里的物品（三下） | 对应 | |
| 9 | U4 教室物品词汇（classroom/desk/door/chair/blackboard/floor） | cne_p058 教室物品（三下）+ cne_p044 房间里的物品（三下） | 对应 | 两点拼合；floor 项目未收 |
| 10 | U4 值日与打扫（clean, on duty） | cne_p060 教室里的建议（三下，Let's 擦黑板等） | 相近 | 值日概念与 clean/on duty 词汇项目没有 |
| 11 | U5 五官词汇（face/eye/ear/nose/mouth） | cne_p013 身体部位（三下，词汇） | 对应 | 项目该点缺 ear |
| 12 | U5 介绍五官 | cne_p015 介绍身体部位（三下）+ cne_p016 读懂五官介绍（三下） | 对应 | |
| 13 | U6 家庭成员词汇（family/mum/dad/brother/sister） | cne_p035 家庭成员（三上，词汇） | 对应 | 称呼差异：沪教用 mum/dad，项目用 father/mother |
| 14 | U6 介绍家人、询问是谁 | cne_p037 介绍家人（三上）+ cne_p036 Who is 询问是谁（三上）+ cne_p038 读懂家人介绍（三上） | 对应 | |
| 15 | U6 情感词 love/warm/happy | — | 无 | warm 项目只作天气义（cne_p092 四上）；love/happy 小学段未收 |
| 16 | U7 动物词汇（dog/cat/hen/horse/bee） | cne_p017 动物（三上，cat/dog/bird/duck）+ cne_p096 农场（四下，含 horse） | 相近 | hen、bee 项目小学段未收 |
| 17 | U7 介绍动物 | cne_p018 用 This is a 介绍动物（三上）+ cne_p019 读懂动物句子（三上） | 对应 | |
| 18 | U8 故事动作短语（fly away/come back/flap wings；bird/hill） | — | 无 | 项目无动作短语/故事表演类知识点（bird 本身在 cne_p017） |
| 19 | U9 can 说能力（Yes, I can!） | cne_p122 can 表示能力（五上，语法）+ cne_p123 谈论会做的事（五上） | 对应（跨年级） | 内容在项目五年级，一年级使用须降阶或建初阶节点 |
| 20 | U9 生活技能动作（wash/tie shoelaces/take a photo） | — | 无 | 项目无生活技能动作词汇 |
| 21 | U10 数字 1–6 | cne_p024 1 到 10（三上，词汇） | 对应 | 范围差：沪教一上只到 6，项目点为 1–10 |
| 22 | U10 数数/找数字活动 | cne_p026 How many 问数量（三上，语法） | 相近 | 项目侧重「问数量」，沪教侧重认数与数数 |

汇总：22 条 —— 对应 12、相近 5、无 4、待核 1。引用到的 20 个项目知识点已逐个回 topics.json 核对名称/年级/描述，全对。

## 反向缺口（沪教一上有、项目完全没有）→ fork 新建候选

按项目命名/domain 惯例拟名，年级记一年级上：

1. **询问名字**（日常表达）——What's your name? / I'm…（与 #4 自我介绍配套）
2. **分时段问候词**（词汇）——morning / afternoon / evening 的问候用法
3. **值日与打扫教室**（词汇+日常表达）——clean、on duty 及教室内劳动指令
4. **情感词**（词汇）——love、happy、warm（情感义）
5. **故事动作短语**（词汇）——fly away、come back、flap wings（U8 故事表演配套）
6. **生活技能动作**（词汇）——wash、tie shoelaces、take a photo
7. 零星补词：pencil case、floor、ear、hen、bee、welcome ——并入相邻词汇点即可，不单独立点。

另：**can 句型**（#19）项目有但压在五年级——若给一年级用，建议在 fork 里建一个初阶「can 说会做的事」（日常表达）节点，与 cne_p122 建先修关系，而不是直接挪用五年级点。

## 落地方式（与数学映射同一条路）

- 数据形态：仿数学 `mappings-hujiao-math.json`，出 `mappings-hujiao-english.json`（沪教册次/Unit → 项目 topicId + 判定 + 备注），将来并入 PR 或单独提 Issue/PR 给作者（作者的版本映射层 Issue #11 是统管口子）。
- 给小朋友摸底的实际用法：一年级上 10 个 Unit 中，7 个 Unit 的核心内容能在项目里找到现成题（走对应点，题面难度按三上/三下，偏难，使用时要降难度预期）；U8 故事表演、U9 生活技能、问名字、情感词四处项目无题，须自出。
