# aiPromo AI 接入说明

本文件梳理了项目中 AI 相关的接口、提示词与可配置项，方便根据业务需求快速调整。

## 1. API 入口

| API | 文件 | 说明 |
| --- | --- | --- |
| `POST /api/analyze` | `backend/app/main.py` → `analyze_product` | 输入产品信息，调用大模型生成痛点/卖点卡片与多渠道文案 |
| `POST /api/generate_script` | `backend/app/main.py` → `generate_video_script` | 针对用户采纳的卡片，生成结构化分镜脚本 |
| `POST /api/generate_video` | `backend/app/main.py` → `generate_video_assets` | 目前生成文本占位文件，待接入真实 TTS/视频服务 |

## 2. Prompt 配置位置

| 场景 | Prompt 常量 | 文件 | 作用 |
| --- | --- | --- | --- |
| 痛点卡片分析 | `ANALYSIS_PROMPT` | `backend/app/services/ai.py` | 负责指导模型根据产品信息输出 `cards` 列表 |
| 分镜脚本生成 | `SCRIPT_PROMPT` | `backend/app/services/ai.py` | 指导模型按照指定视频风格与配音设定输出 `scenes` |
| 系统角色设定 | `SYSTEM_PROMPT` | `backend/app/services/ai.py` | 定义模型整体语气与角色，让输出更贴合 B 端策略 |

> 调整提示词 → 直接修改上述常量即可；若需替换为其他语言或场景，可新增额外模板并在调用处切换。

## 3. LLM 客户端配置

实现文件：`backend/app/services/llm.py`

- 默认使用 OpenAI 兼容接口（chat completions），从环境变量读取配置：
  - `OPENAI_API_KEY`：**必填**，未配置时系统会自动 fallback 到内置模版。
  - `OPENAI_BASE_URL`：可选，支持切换到私有化网关或 Azure OpenAI，默认 `https://api.openai.com/v1`。
  - `OPENAI_MODEL`：模型名，默认 `gpt-4o-mini`，可根据账号权限调整。
  - `OPENAI_TIMEOUT`：接口超时秒数，默认 45 秒。

如需替换为其他厂商（Moonshot、百川、智谱等），仅需修改 `LLMClient.chat` 的请求 URL 和 payload。

## 4. 数据解析与兜底

- `_parse_llm_cards` / `_parse_llm_script`：负责把模型返回的 JSON 转为业务模型；字段缺失时会回退到模版。
- `_fallback_cards` / `_fallback_script`：在模型不可用或解析失败时兜底生成可用内容，保证接口稳定。

## 5. 前端读取位置

- `frontend/src/api.ts`: 调用 `POST /api/analyze`、`POST /api/generate_script`、`POST /api/generate_video`。
- `frontend/src/components/AnalysisPanel.tsx`: 展示 AI 卡片并支持「采纳」与「保存文案」。
- `frontend/src/components/VideoConfig.tsx`: 触发脚本/视频生成并展示结果。

## 6. 自定义建议

1. **多模型策略**：可在 `LLMClient` 中根据不同的 prompt 切换模型（如大模型做分析，小模型做脚本）。
2. **可观测性**：将 `LLMResponse.raw` 日志化或存入数据库，方便后续调试与提示词迭代。
3. **安全处理**：上线前建议增加输出过滤（敏感词/事实校验）以及速率限制。

如需进一步扩展，请结合业务需求在上述文件中继续定制即可。
