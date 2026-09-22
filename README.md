# Medical Agent — Multi-Step Orchestrator


一个基于 **Azure Functions** 的多步医疗对话工作流编排器。

展示三种工作流编排能力：

- **顺序工作流**：症状分析 → 药品查询 → 预约
- **条件工作流**：紧急症状触发短路，跳过后续 3 步
- **会话状态管理**：Azure Blob Storage 持久化，跨调用累积症状历史

---

## 架构

```
用户输入（症状）
      │
      ▼
┌─────────────────────────────────┐
│  Orchestrator (Python)          │
│  - 显式状态管理                 │
│  - 条件分支 / 短路              │
│  - 事件审计日志                 │
└──┬──────┬──────┬──────┬─────────┘
   │      │      │      │
   ▼      ▼      ▼      ▼
[紧急检测] [症状分析] [药品查询] [预约]
   │      │      │      │
   └──────┴──────┴──────┘
          │
          ▼
    Azure Functions
    (4 HTTP endpoints)
          │
    ┌─────┴──────┐
    ▼            ▼
Azure OpenAI  openFDA API
          │
          ▼
    Blob Storage
    (session state)
```

---

## 关键设计决策

### 1. 自写 orchestrator，而非用 Agent 内置编排

- **显式控制流**：每个步骤的输入输出都在代码里，易于审计和调试
- **状态在 Blob 存储**：跨实例可共享，不依赖 agent 内部状态
- **条件短路逻辑清晰**：紧急症状的处理是一条 if 语句，而不是依赖模型自己判断

### 2. 会话状态用 Azure Blob Storage

- 数据结构简单（键值对）
- 访问频率低（每轮对话几次读写）
- 无需 CosmosDB 的高并发能力和复杂查询
- 每个 session 一个 JSON 文件，路径 `sessions/{session_id}.json`

### 3. 条件短路优先

- 紧急症状 → 立即返回
- 跳过 `analyze_symptoms`、`drug_lookup`、`schedule_appointment`
- 节省 AI 调用成本（紧急情况不需走 AI 映射）

---

## 三种工作流

### 顺序工作流（非紧急）

```
input_received → emergency_check(no) → symptom_analysis → drug_lookup → appointment → completed
```

### 条件工作流（紧急）

```
input_received → emergency_check(yes) → escalated
```

后续 3 步全部跳过：

```json
"skipped": ["analyze_symptoms", "drug_lookup", "schedule_appointment"]
```

### 多轮对话（同一 session）

```
Turn 1: symptoms_history = ["头痛", "发烧"]
Turn 2: symptoms_history = ["头痛", "发烧", "现在有点咳嗽"]
```

状态跨调用累积，历史事件保留。

---

## 技术栈

| 组件 | 用途 |
|---|---|
| Python 3.11 | Orchestrator 主体 |
| Azure Functions (Consumption, Linux) | 4 个业务端点 |
| Azure OpenAI (gpt-4.1) | 症状 → 药名映射 |
| openFDA Drug Label API | 药品信息查询 |
| Azure Blob Storage | 会话状态持久化 |
| Managed Identity / DefaultAzureCredential | 认证 |

---

## 运行

```bash
# 1. 设置环境变量
cp .env.example .env
# 编辑 .env 填入你的配置

# 2. 安装依赖
pip install -r requirements.txt

# 3. 登录 Azure
az login

# 4. 启动本地 Function App（另开终端）
cd "../Medical Function Groups"
func start

# 5. 运行 orchestrator
python orchestrator.py --new "头痛,发烧" "Tom"
```

---

## 演示场景

```bash
# 场景 1：顺序工作流（非紧急）
python orchestrator.py --new "头痛,发烧" "Tom"

# 场景 2：条件工作流（紧急）
python orchestrator.py --new "胸痛" "Tom"

# 场景 3：多轮对话（复用同一 session_id）
python orchestrator.py sess_96e900b8 "现在有点咳嗽"
```

---

## 未来改进

- 状态迁移到 CosmosDB（高并发场景）
- 并行药品查询（多个药同时查）
- Service Bus + Queue trigger 做异步执行
- 前端页面 + 多轮对话 UI
- 加入 rate limiting 和 cost monitoring