# Demo 数据初始化

本目录提供完全合成的电商私域数据，用于演示 Insight Agent 的 MySQL + Milvus 混合检索，不代表任何真实客户、商家或平台经营结果。

## 初始化 MySQL

按顺序执行：

```bash
mysql -u root -p < scripts/demo/01_schema.sql
mysql -u root -p < scripts/demo/02_seed.sql
mysql -u root -p < scripts/demo/03_view.sql
mysql -u root -p < scripts/demo/04_check.sql
```

默认数据库：`ecommerce_insight`。

统一视图：`ecommerce_insight_document`。

## 最小 .env

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=ecommerce_insight

INSIGHT_VECTOR_ENABLED=false
```

只验证关键词召回时可以保持向量检索关闭。

## 开启 Milvus

```dotenv
INSIGHT_VECTOR_ENABLED=true
MILVUS_URI=http://localhost:19530
MILVUS_DB_NAME=default
MILVUS_INSIGHT_COLLECTION=ecommerce_insight_evidence
INSIGHT_EMBEDDING_MODEL=BAAI/bge-m3
```

同步：

```bash
uv run python scripts/demo/sync_vector.py
```

## Demo Case

启动服务后调用：

```http
GET /api/research/examples
```

选择返回的一个 `query`：

```http
POST /api/research
Content-Type: application/json

{"query":"..."}
```

随后沿用现有 SSE、Host 和 Report 接口观察完整工作流。
