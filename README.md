# 电商规则与口碑研判平台（多 Agent）

本分支将原通用舆情研究项目适配为面向慧策/旺店通类电商 SaaS 业务的规则与口碑研判平台。

## 业务目标

面向产品、客服、实施、客户成功和行业运营团队，融合商家私域反馈与公域信息，回答：

- 平台规则发生了什么变化，对哪些商家/商品/履约环节有影响？
- 客服工单与商家反馈是否出现集中问题？
- 商品评价与公开评论中的口碑问题是否持续升温？
- 竞品在功能、服务、规则适配或市场反馈上有哪些差异？
- 当前更值得关注的是经营风险，还是可转化的产品/运营机会？

## Agent 分工

1. **Insight Agent（商家私域反馈研究）**
   - MySQL 关键词召回 + Milvus 语义召回
   - 数据范围：客服工单、商家反馈、历史问题案例、商品评价/追评
   - 输出：集中诉求、问题热度、历史复现、商品/主题证据

2. **Media Agent（平台规则与口碑公域研究）**
   - comprehensive_search：综合网页检索
   - source_search：电商平台官方规则/公告溯源
   - realtime_search：近一周公开讨论与口碑变化
   - 数据范围：平台公告、规则文档、公开评论、竞品公开信息

3. **Host Agent（跨来源风险/机会研判）**
   - 对齐同章节 Insight / Media 结论
   - 识别一致点、冲突、信息缺口
   - 输出风险信号、机会信号、受影响对象和建议动作

4. **Report Agent（综合研判报告）**
   - 以 Host 结构化研判为结论依据
   - 汇总双 Agent 证据，生成可追溯 Markdown / HTML 报告

## 固定五章

1. 平台规则变化与业务影响
2. 商家反馈与集中诉求
3. 商品口碑与问题趋势
4. 竞品动态与差异
5. 经营风险与机会研判

## 私域数据契约

业务系统不直接依赖 ERP/CRM 各自表结构，而是通过统一视图 `ecommerce_insight_document` 接入：

| 字段 | 含义 |
| --- | --- |
| platform | 来源平台，如 internal_crm / taobao / jd / douyin_ec |
| source_table | 来源类型，如 customer_ticket / merchant_feedback / issue_case / product_review |
| source_id | 原始业务记录 ID |
| content | 用于关键词与语义检索的正文 |
| published_at | Unix 秒级时间戳 |
| likes/comments/shares/collects/replies | 可选互动/反馈指标，无则置 0 |
| hotness_score | 上游计算的问题热度/业务优先级分 |

这样可以把客服、商家反馈、历史案例、商品评价统一成 Agent 可消费的 EvidenceDocument，同时保留原系统来源用于复核。

## 示例研究主题

- 淘宝售后规则调整对服饰类商家的履约与退款风险影响
- 某商品近 30 天差评集中在“发货慢/尺码偏差”，是否形成可复现问题
- 拼多多与抖音电商近期售后规则变化对旺店通商家的差异化影响
- 某竞品 ERP 新增智能审单能力后，商家公开反馈与我方工单诉求有哪些差异

## 运行边界

- Agent 只做研究、研判与建议，不直接修改商品、订单、库存、结算或平台配置。
- 规则事实优先引用平台官方来源；公开讨论不能替代规则原文。
- 私域样本不能外推为全部商家；公域样本不能外推为全部消费者。
- 风险/机会建议必须能回指当前任务证据与 Host 研判。


## Demo 快速启动

仓库已提供完全合成的私域业务数据和 5 个研究 Case。详细步骤见 `scripts/demo/README.md`。

```bash
mysql -u root -p < scripts/demo/01_schema.sql
mysql -u root -p < scripts/demo/02_seed.sql
mysql -u root -p < scripts/demo/03_view.sql
mysql -u root -p < scripts/demo/04_check.sql
```

服务启动后可通过：

```http
GET /api/research/examples
```

直接获取“售后规则变化、履约风险、商品口碑、竞品情报、客服知识缺口”5 类演示题目，再将其中的 `query` 提交到 `POST /api/research`。

完整演示链路：

```text
Demo 研究题目
    │
    ├──────────────┐
    ▼              ▼
Insight Agent   Media Agent
私域混合检索     公域搜索规划
    │              │
    └──SectionReady┘
          │
          ▼
       Host Agent
风险/机会/冲突/建议
          │
          ▼
      Report Agent
   Markdown / HTML
```

Demo 数据均为合成数据，不代表真实客户、商家或经营结果。


## 可视化 Demo 页面

服务启动后直接访问：

```text
http://localhost:5000/demo
```

页面支持：

- 选择 5 个预置电商研究 Case
- 发起 Insight / Media 并行研究
- 通过 SSE 查看 Agent 实时进度
- 查看 Host 同章节风险/机会研判
- 等待研究输入齐备后触发 Report Agent
- 在页面内预览最终 HTML 报告

为了避免前端对“报告未完成”接口反复收到异常，本分支新增：

```http
GET /api/report/generation/{generation_id}/status
```

用于查询 `running / completed / error`。


## Vue 3 正式前端

原 `/demo` 内嵌 HTML/JS 用于验证交互；正式版本已迁移到 `frontend/`，采用 Vue 3 + Vite。

开发模式：

```bash
uv run uvicorn main:app --reload --port 5000

cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173/ui/`。

生产模式执行 `npm run build` 后，FastAPI 会自动挂载 `frontend/dist` 到 `/ui/`。

正式页面新增：
- 五章业务 Tab
- Insight / Media 证据卡片
- 来源与 source_table
- MySQL / Milvus / Web 检索通道
- 命中查询、排序分、热度
- Host 风险 / 机会 / 受影响对象 / 建议动作
- Host 五章增量研判
- Report 最终 HTML 报告预览

详细说明见 `frontend/README.md`。
