import os
from datetime import datetime
from pathlib import Path

# Put your api keys here
APIKeys = {
    "dashscope_api_key": "",
    "serper_api": "",
    "jina_api_key": "",
    "tavily_api_key": "",
    "firecrawl_api_key": ""
}

URLs = {
    "local_jina_read_url": ''
}

LLM_MODEL_NAME = "qwen-max-2025-01-25"  # default is qwen-max-2025-01-25 via dashscope
MAX_ITERATION_ROUNDS = 20

# Search API Choice
WEBSEARCH_API = (
    "custom"  # 枚举 ["local_jina", "custom", "jina", "firecrawl", "tavilly"]
)

## WebSearch hyperparameters
NUM_WEBPAGES = 8  # google_search检索返回url条数
QUERY2URL_TIMEOUT = 15  # query2url_timout超时时间
URL2HTML_TIMEOUT = 15  # url2html_timeout 获取html超时时间
FETCH_SEARCH_CONCURRENCY_LIMIT = 10  # 限制query2url并发数
FETCH_HTML_CONCURRENCY_LIMIT = 100  # 限制url2html并发数

DEFAULT_CLIP_LENGTH_CHINESE = 800
DEFAULT_CLIP_LENGTH_OTHER = 6 * DEFAULT_CLIP_LENGTH_CHINESE
MAX_WEB_CHUNKS = 20
STREAM_DELIMITER = "\**"  # Delimiter used in stream response

# 日志参数
SYSTEM = {"debug": False, "local_test": True}

## Output path
current_date = datetime.now().strftime("%Y-%m-%d")

DEEPRESEARCH_OUTPUT_DIR = Path(f"results/{current_date}/deepresearch")
DEEPRESEARCH_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LLM_OUTPUT_DIR = Path(f"results/{current_date}/llm")
LLM_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

THINKING_STATUS_DIR = Path("data/thinking_status")
THINKING_STATUS_DIR.mkdir(parents=True, exist_ok=True)