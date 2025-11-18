# aiPromo Demo 项目

一个可落地的 AI 驱动营销演示项目，实现以下流程：

1. 输入产品基础信息。
2. AI 自动生成痛点/卖点卡片与营销文案。
3. 选中文案后配置配音与风格。
4. 一键生成分镜脚本、合成配音与简单预览视频。

## 项目结构

```
aiPromo/
├── backend/        # FastAPI 服务：分析、脚本、音视频生成
│   ├── app/
│   └── requirements.txt
└── frontend/       # React + Vite 前端，串起完整体验
    ├── src/
    ├── package.json
    └── vite.config.ts
```

## 快速开始

### 1. 启动后端（FastAPI）

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-xxx             # 配置真实模型
# 可选：export OPENAI_BASE_URL=https://xxx/v1
# 可选：export OPENAI_MODEL=gpt-4o-mini
uvicorn app.main:app --reload --port 8000
```

> 说明：
> - `/api/analyze`、`/api/generate_script` 会优先调用 OpenAI 兼容接口；若未配置 `OPENAI_API_KEY` 会自动退回到内置模板，保证流程可测。
> - `/api/generate_video` 目前输出文本占位文件，方便后续替换为 MoviePy / 第三方视频 API。

生成的占位“视频/音频”会输出到 `backend/app/generated/`，接口会返回 `/generated/...` 可下载链接。

### 2. 启动前端（Vite + React）

在另一个终端窗口中运行：

```bash
cd frontend
npm install
npm run dev
```

默认开发端口 `5173`，跨域代理指向本地 `8000` 后端。

## 关键功能说明

- **/api/analyze**：调用大模型生成 3 张以上痛点卡片，每张包含场景/痛点/解决方案与多渠道营销文案。
- **/api/generate_script**：基于采纳的卡片 + 配音/风格配置，调用大模型生成结构化分镜脚本。
- **/api/generate_video**：目前写入文本占位文件，保留接口协议便于后续对接 TTS/视频服务。

## 演示路径

1. 填写左侧表单点击「AI 分析」。
2. 在右侧卡片中浏览痛点洞察，可随手保存文案。
3. 选择「采纳」一条作为视频主文案，点击「下一步」。
4. 配置配音语言/声线及视频风格，生成脚本与预览视频。
5. 下载生成的 mp4 视频与 mp3 配音文件，交给实际投放。

## 下一步可以扩展

- 替换为真实大模型服务（如 Azure OpenAI）提升内容质量。
- 接入真实 TTS（微软、火山、讯飞等）与模板化视频素材。
- 增加进度轮询/任务队列，支撑长耗时渲染。
- 与 CRM / 营销自动化系统打通，实现批量分发。

更多 Prompt 与接入说明见 `docs/AI_PROMPTS.md`。

祝使用愉快！欢迎按需扩展。
