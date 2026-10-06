# Mini Tool-Using RAG Agent

一个基于 DeepSeek API 的入门级工具调用 Agent。

它支持：

- 多轮对话；
- Function Calling；
- 本地知识库检索；
- 根据资料回答问题并标注来源；
- 简单计算工具；
- API 异常处理。

项目目标不是实现完整生产系统，而是练习一个最小 Agent 闭环：

```text
用户问题
    ↓
模型判断是否需要工具
    ↓
程序执行工具
    ↓
程序把工具结果交回模型
    ↓
模型生成最终回答
```

---

## 功能

### 1. 计算工具

```text
请计算 12 加 30
```

模型会调用 `add` 工具。

```text
请计算 50 减 8
```

模型会调用 `subtract` 工具。

### 2. 本地知识检索

```text
请查资料回答：RAG 是什么？
```

模型会调用 `search_knowledge`，从 `knowledge.md` 中查找片段，再根据片段回答。

回答会尽量标注来源，例如：

```text
[资料7]
```

### 3. 多轮对话

程序保存完整的 `messages` 历史，因此可以追问：

```text
RAG 是什么？
再简单一点
```

---

## 项目结构

```text
python练习文件/
├── agent_demo.py            # 主程序
├── rag_tools.py             # 文档切分和关键词检索
├── knowledge.md             # 本地知识库
├── requirements.txt         # 依赖
├── .env                     # 本地真实配置，不要提交
├── .env.example             # 配置模板
├── .gitignore
├── README.md
├── Python学习总结_基础到FunctionCalling.md
└── tool_call_practice.py    # 学习阶段的工具调用练习
```

---

## 环境要求

- Python 3.10 或更高版本
- DeepSeek API Key
- 能访问 DeepSeek API 的网络环境

---

## 安装依赖

在项目目录中运行：

```powershell
cd "D:\python练习文件"
python -m pip install -r requirements.txt
```

当前依赖：

```text
requests
python-dotenv
```

---

## 配置环境变量

复制配置模板：

```powershell
Copy-Item .env.example .env
```

如果 `.env` 已经存在，就直接编辑它。

填写：

```text
LLM_API_KEY=你的DeepSeek密钥
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

说明：

- `LLM_API_KEY`：你的真实 API Key；
- `LLM_BASE_URL`：API 地址；
- `LLM_MODEL`：模型名称，以 DeepSeek 平台当前可用模型为准。

安全提醒：

```text
不要把 .env 发到聊天、群聊或 GitHub。
如果 Key 泄露，立即到 DeepSeek 平台删除旧 Key 并创建新 Key。
```

---

## 运行项目

```powershell
cd "D:\python练习文件"
python -X utf8 agent_demo.py
```

启动后会看到：

```text
Agent Demo 已启动。输入 exit 退出。
可以尝试：请查资料回答：RAG 是什么？
可以尝试：请计算 12 加 30。
```

---

## 示例

### 示例 1：计算

输入：

```text
请计算 12 加 30
```

流程：

```text
用户问题
    ↓
模型调用 add
    ↓
程序执行 add(12, 30)
    ↓
工具结果 42 返回给模型
    ↓
模型回答
```

### 示例 2：RAG

输入：

```text
请查资料回答：RAG 是什么？
```

流程：

```text
用户问题
    ↓
模型调用 search_knowledge
    ↓
程序读取 knowledge.md
    ↓
关键词检索相关资料
    ↓
资料片段交回模型
    ↓
模型根据资料回答并标注来源
```

---

## 核心代码流程

### 1. 配置读取

```python
load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL")
MODEL = os.getenv("LLM_MODEL")
```

### 2. 发送请求

```python
response = requests.post(
    URL,
    headers=HEADERS,
    json=payload,
    timeout=60,
)
response.raise_for_status()
data = response.json()
```

### 3. 处理工具调用

```python
message = result["choices"][0]["message"]
tool_calls = message.get("tool_calls")
```

### 4. 执行工具

```python
if function_name == "add":
    return add(arguments["a"], arguments["b"])

if function_name == "subtract":
    return subtract(arguments["a"], arguments["b"])

if function_name == "search_knowledge":
    return search_knowledge(arguments["keyword"])
```

### 5. 把工具结果交回模型

```python
messages.append({
    "role": "tool",
    "tool_call_id": tool_call["id"],
    "content": str(tool_result),
})
```

---

## 知识库说明

当前知识库是：

```text
knowledge.md
```

`rag_tools.py` 会：

1. 读取 Markdown 文件；
2. 按空行切分；
3. 为每个片段编号；
4. 用关键词匹配查找相关片段。

例如：

```python
chunks = load_chunks("knowledge.md")
found_chunks = search_chunks(chunks, "RAG")
```

目前是简单关键词检索，不是向量检索。

---

## 当前限制

这是学习版本，不是生产版本。

- 检索使用关键词匹配，不是 Embedding；
- 没有使用 FAISS、Milvus 等向量数据库；
- 没有完整评测集；
- 没有多智能体协作；
- 没有 MCP 工具服务；
- 对话历史会一直保存在内存中，程序重启后丢失；
- 错误处理比较基础；
- 没有用户界面，只有命令行。

---

## 下一步改进

1. 把关键词检索升级为 Embedding + FAISS；
2. 增加知识库引用页码或段落编号；
3. 增加 20 到 30 条评测问题；
4. 统计回答正确率、检索命中率和工具调用成功率；
5. 将工具定义移到单独模块；
6. 增加最大 token 和成本统计；
7. 增加更完善的异常处理和日志；
8. 把知识库和工具封装成 MCP Server；
9. 增加简单的 Web 界面；
10. 上传 GitHub 并补充演示视频。

---

## 学习重点

这个项目最重要的不是代码量，而是理解：

```text
模型负责判断和生成
程序负责执行和提供真实数据
工具负责完成确定性任务
RAG 负责把外部知识带进上下文
```

如果要展示项目，建议按以下顺序讲解：

1. 用户输入问题；
2. 模型决定是否调用工具；
3. 程序执行工具；
4. 工具结果被追加到消息历史；
5. 模型基于工具结果生成最终回答；
6. RAG 如何检索资料并标注来源；
7. 当前限制和下一步改进。
