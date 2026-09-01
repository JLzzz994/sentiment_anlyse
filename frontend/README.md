# Vue 3 正式前端

## 开发模式

先启动 FastAPI：

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

再启动 Vue：

```bash
cd frontend
npm install
npm run dev
```

访问：

```text
http://localhost:5173/ui/
```

Vite 会将 `/api/*` 代理到 `http://localhost:5000`。

## 生产构建

```bash
cd frontend
npm install
npm run build
cd ..
uv run uvicorn main:app --host 0.0.0.0 --port 5000
```

FastAPI 检测到 `frontend/dist` 后会自动挂载：

```text
http://localhost:5000/ui/
```

## 页面数据接口

- `GET /api/research/examples`：预置研究 Case
- `POST /api/research`：启动研究任务
- `GET /api/events/stream?task_id=...`：Agent SSE 进度
- `GET /api/research/evidence?task_id=...`：章节证据卡片
- `GET /api/host/judgements?task_id=...`：Host 五章结构化研判
- `GET /api/report/status?task_id=...`：综合报告输入状态
- `POST /api/report/generate`：生成综合报告
- `GET /api/report/generation/{generation_id}/status`：报告生成状态
- `GET /api/report/result/{generation_id}`：HTML 报告预览
