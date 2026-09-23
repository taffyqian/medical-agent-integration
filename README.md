# Medical Agent — Multi-Step Orchestrator

🚀 **Live Demo**: https://medical-agent-integration-mzzibraay3vlgkyzyjxeg5.streamlit.app

一个基于 **Azure Functions + Streamlit** 的多步医疗对话工作流。用户输入症状，系统自动完成：**紧急检测 → 症状分析 → 药品查询 → 预约安排**，并支持多轮会话、条件短路、会话状态持久化。

---

## 目录

- [核心功能](#核心功能)
- [架构](#架构)
- [技术栈](#技术栈)
- [运行](#运行)
- [工作流示例](#工作流示例)
- [关键设计决策](#关键设计决策)
- [项目结构](#项目结构)
- [未来改进](#未来改进)
- [免责声明](#免责声明)

---

## 核心功能

- **条件短路（Conditional Short-circuit）**：紧急症状（胸痛、呼吸困难等）命中关键词后**跳过 AI 分析和药品推荐**，直接展示急救电话
- **会话状态管理**：Azure Blob Storage 持久化，支持多轮症状累积与历史回溯
- **AI 生成内容**：基于 Azure OpenAI（gpt-4.1）生成**症状分析、可能原因、用药建议**
- **第三方数据集成**：调用 **openFDA** 获取药品 FDA 标签与警告
- **可审计事件流**：每一步（紧急检测 / 症状分析 / 药品查询 / 预约）记录时间戳
- **三语支持**：简体中文 / 繁体中文 / English
- **对话总结**：多轮后自动汇总症状、严重程度、可能原因、药品、预约

---

## 架构

```
┌──────────────────────────────────────────────────────┐
│          Streamlit UI (chat-style)                    │
│          https://medical-agent-xxx.streamlit.app      │
└────────────────────────┬─────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│              Orchestrator (Python)                    │
│   · 显式状态管理（Blob Storage）                       │
│   · 条件分支 / 短路                                    │
│   · 事件审计日志                                       │
└────────────────────────┬─────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌────────┐    ┌────────────┐   ┌──────────────┐
    │ Azure  │    │  openFDA   │   │  Blob Storage│
    │ OpenAI │    │    API     │   │ (session)    │
    └────────┘    └────────────┘   └──────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   Azure Functions    │
              │   (4 endpoints)      │
              │   · analyze_symptoms │
              │   · drug_lookup      │
              │   · schedule_appt    │
              │   · emergency_esc    │
              └──────────────────────┘
```

---

## 技术栈

| 组件 | 用途 |
|---|---|
| **Python 3.11** | 应用主体 |
| **Streamlit** | 前端 UI（chat-style） |
| **Azure Functions** | 4 个 serverless 端点 |
| **Azure OpenAI (gpt-4.1)** | 症状分析、可能原因、用药建议生成 |
| **Azure Blob Storage** | 会话状态持久化 |
| **openFDA Drug Label API** | 药品 FDA 数据 |
| **Streamlit Cloud** | 公网托管 |

---

## 运行

### 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量（.env）
cat > .env <<'EOF'
FUNCTION_BASE=https://your-function-app.azurewebsites.net/api
FUNCTION_APP_KEY=your-host-key
STORAGE_ACCOUNT_URL=https://your-storage.blob.core.windows.net/
SESSION_CONTAINER=sessions
EOF

# 3. 登录 Azure（用于 Blob 的 DefaultAzureCredential）
az login

# 4. 启动 Streamlit
streamlit run app.py
```

### 云端（Streamlit Cloud）

**Secrets 配置**（在 Streamlit Cloud 应用的 Settings → Secrets）：

```toml
FUNCTION_BASE = "https://your-function-app.azurewebsites.net/api"
FUNCTION_APP_KEY = "your-host-key"
STORAGE_ACCOUNT_URL = "https://your-storage.blob.core.windows.net/"
SESSION_CONTAINER = "sessions"
SESSION_STORAGE_CONN = "DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net"
```

**注意**：云端用连接字符串（`SESSION_STORAGE_CONN`），本地用 `DefaultAzureCredential`。

---

## 工作流示例

### 顺序工作流（非紧急）

```
input_received
  → emergency_check (no)
  → symptom_analysis
  → drug_lookup
  → appointment
  → completed
```

### 条件工作流（紧急）

```
input_received
  → emergency_check (yes)
  → escalated  （跳过 analyze_symptoms / drug_lookup / schedule_appointment）
```

### 多轮对话（同一 session）

```
Turn 1: symptoms_history = ["头痛", "发烧"]
Turn 2: symptoms_history = ["头痛", "发烧", "喉咙痛"]
```

状态跨调用累积，历史事件保留。

---

## 关键设计决策

### 1. 条件短路优先于顺序执行

- **紧急症状 → 立即返回**，跳过 AI 分析和药品推荐
- **节省 AI 调用成本**（紧急情况无需走 AI 映射）
- **避免误导**：紧急情况不应该展示 OTC 建议

### 2. 会话状态用 Azure Blob Storage

- 数据结构简单（键值对）
- 访问频率低（每轮对话几次读写）
- 无需 CosmosDB 的高并发能力
- 每 session 一个 JSON 文件：`sessions/{session_id}.json`

### 3. AI 生成 + 预置映射混合

- **常见症状**（头痛、发烧等）→ 命中本地 `_PRESET`，快速返回
- **未知症状** → 调 AI 生成药名 + 可能原因 + 用药建议
- **AI 兜底判断**：即使命中预置，也调 AI 生成 `possible_causes`

### 4. 双通道 Blob 访问

- **本地开发**：`DefaultAzureCredential`（Azure CLI 凭证）
- **云端部署**：`SESSION_STORAGE_CONN` 连接字符串（Streamlit Cloud 无 MI）
- 代码根据环境变量自动选择

---

## 项目结构

```
.
├── app.py                  # Streamlit 入口
├── orchestrator.py         # 多步工作流编排器
├── ui_components.py        # UI 组件（侧边栏、进度条、结果卡片）
├── ui_texts.py             # i18n 文案字典（中/繁/英）
├── ui_helpers.py           # 时间格式化、FDA 警告格式化
├── ui_styles.py            # 全局 CSS
├── requirements.txt        # 依赖
├── startup.sh              # App Service 启动脚本
└── README.md
```

---

## 未来改进

- **Agent 集成**：将 4 个端点挂载到 Azure AI Foundry Agent，通过 OpenAPI Tools 实现自然语言对话
- **状态迁移到 CosmosDB**（高并发场景）
- **并行药品查询**（多药同时查）
- **CI/CD**：GitHub Actions 自动部署
- **意图识别路由**：区分"症状描述"与"自然语言提问"

---

## 免责声明

本工具仅用于演示和技术验证，**不构成医疗建议**。用药前请咨询专业医师或药师。