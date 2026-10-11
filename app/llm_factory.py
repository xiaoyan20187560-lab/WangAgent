
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel
import os


def get_llm() -> BaseChatModel:
    # 确保在读取环境变量前加载 .env
    from pathlib import Path
    from dotenv import load_dotenv

    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path, override=True)

    # 1. 在函数内部读取环境变量
    BASE_URL = os.getenv(
        "DEEPSEEK_BASE_URL"
    )
    DEEPSEEK_API_KEY = os.getenv(
        "DEEPSEEK_API_KEY"
    )

    # 2. 检查必要的配置是否存在
    if not DEEPSEEK_API_KEY:
        raise ValueError("未设置 DEEPSEEK_API_KEY，请检查 .env 文件。")
    if not BASE_URL:
        raise ValueError("未设置 DEEPSEEK_BASE_URL，请检查 .env 文件。")

    llm = init_chat_model(
        model="deepseek-v4-flash-0731",
        model_provider="openai",
        base_url=BASE_URL,
        api_key=DEEPSEEK_API_KEY,
    )


    return llm
if __name__ == "__main__":
    llm = get_llm()
    print(llm)
    print("LLM 初始化成功")
    response = llm.invoke("你好，请只回复：连接成功")
    print(response.content)

