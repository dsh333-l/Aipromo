# aiPromo Demo 项目

一个可落地的 AI 驱动营销演示项目，实现以下流程：

1. 输入产品基础信息。
2. AI 自动生成痛点/卖点卡片与营销文案（真实大模型）。
3. 选中文案后配置配音与风格。
4. 生成分镜脚本，并调用 HeyGen（如已配置）生成视频；本地同时写入占位文件。

## 项目结构

```
aiPromo/
├── backend/        # FastAPI 服务：分析、脚本、视频生成接口
│   ├── app/
│   └── requirements.txt
├── frontend/       # React + Vite 前端，串起完整体验
└── docs/           # Prompt & 第三方服务说明
```

## 快速开始

### 1) 启动后端（FastAPI）

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-xxx             # 必填：大模型
# 可选：export OPENAI_BASE_URL=https://xxx/v1
# 可选：export OPENAI_MODEL=gpt-4o-mini
# 可选：export HEYGEN_API_KEY=xxxxx       # 配置后会将分镜推送到 HeyGen 生成视频
uvicorn app.main:app --reload --port 8000
```

> 说明：
> - `/api/analyze`、`/api/generate_script` 会优先调用 OpenAI 兼容接口；未配置 `OPENAI_API_KEY` 时回退到内置模板。
> - `/api/generate_video` 会尝试调用 HeyGen；未配置或失败时写入占位文件（含脚本/调用信息）到 `backend/app/generated/`。

### 2) 启动前端（Vite + React）

```bash
cd ../frontend
npm install
npm run dev
```

默认开发端口 `5173`，跨域代理指向本地 `8000` 后端。

## 关键接口

- `POST /api/analyze`：调用大模型生成 3 条以上痛点卡片（场景/痛点/解决方案/多渠道文案）。
- `POST /api/generate_script`：基于采纳的卡片 + 配音/风格配置，调用大模型生成分镜脚本。
- `POST /api/generate_video`：优先推送 HeyGen（如配置），同时写入本地占位文本文件。

## 演示路径

1. 填写左侧表单点击「AI 分析」。
2. 在右侧卡片中浏览痛点洞察，可保存/采纳。
3. 点击「下一步」进入视频配置，选择配音与风格。
4. 生成分镜脚本并触发视频生成；若配置 HeyGen，前端会得到 HeyGen 链接。

## 参考文档

- Prompt 和 LLM 接入说明：`docs/AI_PROMPTS.md`
- HeyGen 调用说明：`docs/HEYGEN.md`

## 可扩展方向

- 接入真实 TTS/素材库，替换本地占位文件。
- 增加任务队列与回调，支撑长耗时渲染。
- 加入内容安全/事实校验，面向生产环境。
