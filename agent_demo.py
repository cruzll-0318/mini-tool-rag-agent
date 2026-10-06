import json
import os

import requests
from dotenv import load_dotenv

from rag_tools import load_chunks, search_chunks

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL")
MODEL = os.getenv("LLM_MODEL")

URL = BASE_URL.rstrip("/") + "/chat/completions" if BASE_URL else ""
KNOWLEDGE_PATH = "knowledge.md"
MAX_STEPS = 5

HEADERS = {
    "Authorization": "Bearer " + (API_KEY or ""),
    "Content-Type": "application/json",
}

SYSTEM_PROMPT = (
    "你是一个严格依据本地知识库回答问题的助手。"
    "遇到 API、RAG、Function Calling、.env、类和对象等知识库问题时，"
    "必须先调用 search_knowledge 工具查找资料。"
    "知识库回答只能使用 search_knowledge 返回的资料，不得添加外部知识。"
    "知识库事实句必须标注资料编号，例如 [资料7]。"
    "涉及计算时，使用 add 或 subtract 工具。"
    "资料不足时，直接回答“资料中没有足够信息”。"
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "计算两个数字的和。",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "第一个数字"},
                    "b": {"type": "number", "description": "第二个数字"},
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "subtract",
            "description": "计算两个数字的差。",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "第一个数字"},
                    "b": {"type": "number", "description": "第二个数字"},
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "当用户询问本地知识库中的内容时，搜索相关资料。",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "要搜索的关键词",
                    },
                },
                "required": ["keyword"],
            },
        },
    },
]


def check_config():
    missing = []

    if not API_KEY:
        missing.append("LLM_API_KEY")
    if not BASE_URL:
        missing.append("LLM_BASE_URL")
    if not MODEL:
        missing.append("LLM_MODEL")

    if missing:
        print("缺少配置：", ", ".join(missing))
        print("请根据 .env.example 创建 .env 并填写配置。")
        return False

    return True


def ask_llm(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS,
        "temperature": 0.2,
    }

    try:
        response = requests.post(
            URL,
            headers=HEADERS,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        print("请求超时。")
        return None

    except requests.exceptions.HTTPError:
        print("HTTP 错误：", response.text)
        return None

    except (KeyError, IndexError, ValueError):
        print("返回数据格式错误。")
        return None

    except requests.exceptions.RequestException as error:
        print("网络错误：", error)
        return None


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def search_knowledge(keyword):
    chunks = load_chunks(KNOWLEDGE_PATH)
    found_chunks = search_chunks(chunks, keyword)

    if not found_chunks:
        return "没有找到相关资料。"

    result = (
        "以下资料是唯一允许使用的事实来源。"
        "只能根据这些资料回答，不得使用外部知识补充。"
        "每个事实句必须标注资料编号，例如 [资料7]。\n\n"
    )

    for chunk in found_chunks:
        result += "[资料" + str(chunk["id"]) + "]\n"
        result += chunk["text"] + "\n\n"

    return result


def execute_function(tool_call):
    function_name = tool_call["function"]["name"]
    arguments = json.loads(tool_call["function"]["arguments"])

    if function_name == "add":
        return add(arguments["a"], arguments["b"])

    if function_name == "subtract":
        return subtract(arguments["a"], arguments["b"])

    if function_name == "search_knowledge":
        return search_knowledge(arguments["keyword"])

    return "未知工具：" + function_name


def run_agent(messages):
    for _ in range(MAX_STEPS):
        result = ask_llm(messages)

        if result is None:
            return "请求失败，请稍后再试。"

        message = result["choices"][0]["message"]
        tool_calls = message.get("tool_calls")

        if not tool_calls:
            messages.append(message)
            return message.get("content") or "模型没有返回文本。"

        messages.append(message)

        for tool_call in tool_calls:
            tool_result = execute_function(tool_call)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": str(tool_result),
            })

    return "达到最大工具调用次数。"


def main():
    if not check_config():
        return

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    print("Agent Demo 已启动。输入 exit 退出。")
    print("可以尝试：请查资料回答：RAG 是什么？")
    print("可以尝试：请计算 12 加 30。")

    while True:
        user_input = input("\n你：")

        if user_input.strip().lower() == "exit":
            print("已退出。")
            break

        if user_input.strip() == "":
            continue

        messages.append({"role": "user", "content": user_input})
        answer = run_agent(messages)
        print("助手：", answer)


if __name__ == "__main__":
    main()
