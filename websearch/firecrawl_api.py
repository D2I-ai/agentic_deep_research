import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

import aiohttp
import requests

from _setting import *
from tools.log import logger_instance as logger
from websearch.utils import (
    firecrawl_read_response_parse,
    firecrawl_search_response_parse,
    merge_final_data,
    save_to_json,
)


async def firecrawl_search_request(query, session, timeout: int = 20):
    """
    Asynchronously perform firecrawl search
    """
    start_time = time.monotonic()

    # API配置
    url = "https://api.firecrawl.dev/v1/search"
    headers = {
        "Authorization": f"Bearer {APIKeys['firecrawl_api_key']}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": query,
        "limit": 5,
        "tbs": "qdr:d",
        "timeout": 60000,
        "ignoreInvalidURLs": False,
        "scrapeOptions": {
            "onlyMainContent": True,
            "includeTags": [],
            "excludeTags": [],
            "maxAge": 0,
            "headers": {},
            "waitFor": 0,
            "mobile": False,
            "skipTlsVerification": False,
            "timeout": 30000,
            "parsePDF": True,
            "location": {"country": "US", "languages": ["en-US"]},
            "removeBase64Images": True,
            "blockAds": True,
            "proxy": "basic",
            "storeInCache": True,
            "formats": [],
        },
    }
    try:

        async with session.post(
            url, json=payload, headers=headers, timeout=timeout
        ) as response:
            total_time = time.monotonic() - start_time

            if response.status == 200:
                response_data = await response.json()
                data = response_data.get("data", [])

                ready_data = firecrawl_search_response_parse(data)

                logger.info(
                    f"firecrawl_search 成功 | "
                    f"查询: '{query[:30]}...' | "
                    f"结果数: {len(data)} | "
                    f"耗时: {total_time:.3f}秒"
                )
                return ready_data
            else:

                error_text = await response.text()
                logger.error(
                    f"请求失败 | 查询: '{query}' | "
                    f"状态码: {response.status} | "
                    f"响应: {error_text[:200]} | "
                    f"耗时: {total_time:.3f}秒"
                )
                return None
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.error(f"Error in '{query}' |  {str(e)}")
        return None


async def firecrawl_search_async(query):
    """
    Asynchronously perform firecrawl search (supports batch queries)
    """

    queries = [query] if isinstance(query, str) else query
    connector = aiohttp.TCPConnector(limit=FETCH_HTML_CONCURRENCY_LIMIT)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [firecrawl_search_request(q, session) for q in queries]
        task_res = await asyncio.gather(*tasks)
    res = merge_final_data(queries, task_res)
    return res


async def firecrawl_read_async(query, parseurl: str, timeout: int = 20):
    start_time = time.monotonic()

    url = "https://api.firecrawl.dev/v1/scrape"
    headers = {
        "Authorization": f"Bearer {APIKeys['firecrawl_api_key']}",
        "Content-Type": "application/json",
    }

    payload = {
        "zeroDataRetention": False,
        "onlyMainContent": True,
        "maxAge": 0,
        "waitFor": 0,
        "mobile": False,
        "skipTlsVerification": False,
        "timeout": 30000,
        "parsePDF": True,
        "location": {"country": "US"},
        "blockAds": True,
        "storeInCache": True,
        "formats": ["markdown"],
        "url": parseurl,
    }

    connector = aiohttp.TCPConnector(limit=FETCH_HTML_CONCURRENCY_LIMIT)
    async with aiohttp.ClientSession(connector=connector) as session:
        try:

            async with session.post(
                url, json=payload, headers=headers, timeout=timeout
            ) as response:
                total_time = time.monotonic() - start_time

                if response.status == 200:
                    response_data = await response.json()
                    data = response_data.get("data", {})

                    ready_data = firecrawl_read_response_parse(data, query)

                    logger.info(
                        f"firecrawl_read 成功 | "
                        f"URL: '{parseurl}' | "
                        f"耗时: {total_time:.3f}秒 | "
                        f"内容长度: {len(str(ready_data))}字节"
                    )

                    return ready_data
                else:

                    error_text = await response.text()
                    logger.error(
                        f"请求失败 | URL: '{parseurl}' | "
                        f"状态码: {response.status} | "
                        f"响应: {error_text[:200]} | "
                        f"耗时: {total_time:.3f}秒"
                    )
                    return None

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"请求异常 | URL: '{parseurl}' | 错误: {str(e)}")
            return None


def firecrawl_read(parseurl):
    """
    Use the FireCrawl API to scrape web content for a specified URL.

    Parameters:
        parseurl (str): The target webpage address to be scraped (required). Example: "https://example.com"

    """
    url = "https://api.firecrawl.dev/v1/scrape"

    payload = {
        "zeroDataRetention": False,
        "onlyMainContent": True,
        "maxAge": 0,
        "waitFor": 0,
        "mobile": False,
        "skipTlsVerification": False,
        "timeout": 30000,
        "parsePDF": True,
        "location": {"country": "US"},
        "blockAds": True,
        "storeInCache": True,
        "formats": ["markdown"],
        "url": parseurl,
    }
    headers = {
        "Authorization": "Bearer " + APIKeys["firecrawl_api_key"],
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    if response.status_code == 200:
        response.encoding = "utf-8"
        data = response.json()["data"]
        ready_data = firecrawl_read_response_parse(data)
        save_to_json(ready_data, "firecrawl_read_test_rst.json")
    else:
        logger.error(f"请求失败，状态码: {response.status_code}")


def firecrawl_search(query):
    """
    Use the FireCrawl API to perform search requests and scrape web content.

    Parameters:
        query (str): The search keyword or question (required). For example: "James historical ranking".

    """

    url = "https://api.firecrawl.dev/v1/search"

    payload = {
        "query": query,
        "limit": 5,
        "tbs": "qdr:d",
        "location": "",
        "timeout": 60000,
        "ignoreInvalidURLs": False,
        "scrapeOptions": {
            "onlyMainContent": True,
            "includeTags": [],
            "excludeTags": [],
            "maxAge": 0,
            "headers": {},
            "waitFor": 0,
            "mobile": False,
            "skipTlsVerification": False,
            "timeout": 30000,
            "parsePDF": True,
            "location": {"country": "US", "languages": ["en-US"]},
            "removeBase64Images": True,
            "blockAds": True,
            "proxy": "basic",
            "storeInCache": True,
            "formats": [],
        },
    }
    headers = {
        "Authorization": "Bearer " + APIKeys["firecrawl_api_key"],
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    if response.status_code == 200:
        response.encoding = "utf-8"
        data = response.json()["data"]
        ready_data = firecrawl_search_response_parse(data)
        save_to_json(ready_data, "firecrawl_search_test_rst.json")
    else:
        logger.error(f"请求失败，状态码: {response.status_code}")


def concurrent_task(task_func, input_list: list, concurrency: int):
    """
    A general-purpose function for executing tasks concurrently.

    This function supports concurrent execution of any FireCrawl-related tasks (e.g., [firecrawl_search](file://d:\code\AskNBA\websearch\firecrawl_api.py#L278-L307) or [firecrawl_read](file://d:\code\AskNBA\websearch\firecrawl_api.py#L156-L189)).

    Args:
        task_func (function): The task function to execute concurrently, such as [firecrawl_search](file://d:\code\AskNBA\websearch\firecrawl_api.py#L278-L307) or [firecrawl_read](file://d:\code\AskNBA\websearch\firecrawl_api.py#L156-L189).
        input_list (list): A list of input parameters required by the task function, where each element is a parameter (e.g., search keywords or URLs).
        concurrency (int): The number of concurrent threads, controlling how many tasks are executed simultaneously.

    """
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(task_func, item) for item in input_list]
        for future in futures:
            future.result()


def concurrent_firecrawl_search(questions: list, concurrency: int = 4):
    """
    Execute FireCrawl search requests concurrently to improve efficiency.

    Args:
        questions (list): A list of search keywords, where each element is a string.
                          Example: ["LeBron James ranking", "Latest Warriors news"]
        concurrency (int): The number of concurrent threads, controlling how many search tasks are executed simultaneously.

    """
    concurrent_task(firecrawl_search, questions, concurrency)


def concurrent_firecrawl_read(urls: list, concurrency: int = 4):
    """
    Execute FireCrawl web scraping requests concurrently to improve efficiency.

    This function uses a thread pool to execute multiple [firecrawl_read](file://d:\code\AskNBA\websearch\firecrawl_api.py#L156-L189) requests concurrently, suitable for scenarios where bulk web content needs to be scraped.

    Args:
        urls (list): A list of target web page URLs, where each element is a string.
                     Example: ["https://example.com/page1", "https://example.com/page2"]
        concurrency (int): The number of concurrent threads, controlling how many scraping tasks are executed simultaneously.

    """
    concurrent_task(firecrawl_read, urls, concurrency)


if __name__ == "__main__":
    # Test firecrawl search
    # question = "詹姆斯历史排名"
    # firecrawl_search(question)

    # Test firecrawl read
    # url = "https://docs.firecrawl.dev/features/scrape"
    # firecrawl_read(url)

    # Test cases for QUESTION LIST
    # nba_questions = [
    #     "NBA历史上得分榜排名第一的球员是谁？",
    #     "哪支球队赢得过最多的NBA总冠军？",
    #     "Who is the leading scorer in NBA history?",
    #     "Which team has won the most NBA championships?"
    # ]
    #
    # concurrent_firecrawl_search(nba_questions)

    # Test cases for URL LIST
    nba_urls = [
        "https://www.aibase.com/zh/news/19787",
        "https://www.aibase.com/zh/news/19786",
        "https://www.aibase.com/zh/news/19785",
        "https://www.aibase.com/zh/news/19784",
    ]
    concurrent_firecrawl_read(nba_urls)
