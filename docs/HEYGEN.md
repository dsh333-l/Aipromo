# HeyGen 视频生成接入

本项目已在后端保留了 HeyGen API 的调用入口，用于将生成的分镜脚本推送到 HeyGen 生成视频。当前仍会写入本地占位文件，但若配置了密钥会优先触发 HeyGen 生成。

## 环境变量

- `HEYGEN_API_KEY`：必填，HeyGen 提供的 API Key。
 - `HEYGEN_API_URL`：可选，默认 `https://api.heygen.com/v2/video/generate`（官方示例接口；如变更请以最新文档为准）。
 - `HEYGEN_STATUS_URL`：可选，默认 `https://api.heygen.com/v1/video_status.get?video_id=`。
 - `HEYGEN_TEMPLATE_ID`：可选，绑定到特定模板（若需要）。
 - `HEYGEN_AVATAR_ID`：可选，指定数字人形象，未设置默认使用官方 demo `Lina_Dress_Sitting_Side_public`。
 - `HEYGEN_AVATAR_STYLE`：可选，默认 `normal`。
 - `HEYGEN_VOICE_ID`：可选，指定配音 ID，未设置默认使用官方 demo `119caed25533477ba63822d5d1552d25`。
 - `HEYGEN_CALLBACK_URL`：可选，生成完成后的回调地址。
 - `HEYGEN_TEST_MODE`：可选，设为 `true` 切换到测试模式（如果 HeyGen 支持）。
 - `HEYGEN_BACKGROUND_MUSIC_ID`：可选，设置背景音乐。

## 代码入口

- 调用位置：`backend/app/services/video.py` 的 `_call_heygen`。
- 负责编排 payload 的函数：`_build_heygen_payload`。
- 最终入口：`generate_video_assets`，优先调用 HeyGen，失败/未配置时写入占位文件。

## 注意事项

1. v2 接口要求 `video_inputs`，默认使用 avatar+text voice；可在 `_build_heygen_payload` 调整角色/素材字段。
2. 返回的 `video_url` 可能是下载地址或状态查询地址（若返回 video_id 则拼接 `HEYGEN_STATUS_URL`）。前端会通过 `/api/video_status?video_id=xxx` 轮询状态。
3. 每次调用会在 `backend/app/generated/heygen_debug_<timestamp>.json` 写入请求/响应或错误信息，便于排查（遇到 4xx 多为参数或权限问题）。
4. 如需在本地落地生成的 mp4，可在回调中主动下载并写入 `backend/app/generated/`，然后返回本地 `/generated/...` 路径。
