import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor

from tavily import TavilyClient

from _setting import *
from tools.log import logger_instance as logger
from websearch.utils import (
    merge_final_data,
    save_to_json,
    tavily_read_response_parse,
    tavily_search_response_parse,
)

if WEBSEARCH_API == "tavily":
    client = TavilyClient(api_key=APIKeys["tavily_api_key"])
else:
    client = None

# 创建线程池执行器
executor = ThreadPoolExecutor(max_workers=FETCH_HTML_CONCURRENCY_LIMIT)


async def tavily_search_request(query: str):
    """
    异步执行 Tavily 搜索
    Asynchronously perform Tavily search
    """
    start_time = time.monotonic()

    try:
        # 在单独线程中执行同步搜索
        # Execute synchronous search in a separate thread
        response = await asyncio.get_event_loop().run_in_executor(
            executor,
            lambda: client.search(
                query=query, include_favicon=True, include_raw_content="text"
            ),
        )

        end_time = time.monotonic()
        elapsed_time = end_time - start_time
        logger.info(f"tavily_search 耗时: {elapsed_time:.4f} 秒")

        data = response["results"]
        ready_data = tavily_search_response_parse(data)
        return ready_data
    except Exception as e:
        logger.error(f"{query} Error in async_tavily_search: {e}")
        return None


async def tavily_search_async(query):
    """
    异步执行 Tavily 搜索（支持批量查询）
    Asynchronously perform Tavily search (supports batch queries)
    """
    # 统一参数类型处理
    # Normalize input to list
    queries = [query] if isinstance(query, str) else query
    tasks = [tavily_search_request(q) for q in queries]
    task_res = await asyncio.gather(*tasks)
    res = merge_final_data(queries, task_res)
    return res


async def tavily_read_async(query, url):
    """
    异步执行 Tavily 网页读取
    Asynchronously extract webpage content using Tavily
    """
    start_time = time.monotonic()
    urls = url if isinstance(url, list) else [url]
    try:
        # 在单独线程中执行同步提取
        # Run synchronous extract in a separate thread
        response = await asyncio.get_event_loop().run_in_executor(
            executor,
            lambda: client.extract(urls=urls, format="text", include_favicon=True),
        )

        end_time = time.monotonic()
        elapsed_time = end_time - start_time
        logger.info(f"tavily_read 耗时: {elapsed_time:.4f} 秒")

        data = response.get("results", [])

        # 解析响应数据
        # Parse response data
        ready_data = tavily_read_response_parse(data, query)
        return ready_data
    except Exception as e:
        logger.error(f"{url} Error in async_tavily_read: {e}")
        return None


def tavily_search(query):
    """
    执行 Tavily 搜索并保存结果到 JSON 文件
    Perform Tavily search and save results to JSON file
    """
    start_time = time.time()  # 记录开始时间
    # Record start time

    response = client.search(
        query=query, include_favicon=True, include_raw_content="text"
    )

    end_time = time.time()  # 记录结束时间
    # Record end time
    elapsed_time = end_time - start_time  # 计算耗时
    # Calculate elapsed time
    logger.info(f"tavily_scrape 耗时: {elapsed_time:.4f} 秒")  # 打印耗时
    # Log time cost

    data = response["results"]
    reday_data = tavily_search_response_parse(data)
    save_to_json(reday_data, "tavily_search_test_rst.json")


def tavily_read(urls):
    """
    使用 Tavily 提取网页内容并保存到 JSON 文件
    Extract webpage content using Tavily and save to JSON file
    """
    if isinstance(urls, str):
        urls = [urls]

    start_time = time.time()  # 记录开始时间
    # Record start time

    response = client.extract(urls=urls, format="text", include_favicon=True)

    end_time = time.time()  # 记录结束时间
    # Record end time
    elapsed_time = end_time - start_time  # 计算耗时
    # Calculate elapsed time
    logger.info(f"tavily_scrape 耗时: {elapsed_time:.4f} 秒")  # 打印耗时
    # Log time cost

    data = response["results"]
    reday_data = tavily_read_response_parse(data)
    save_to_json(reday_data, "tavily_read_test_rst.json")


def tavily_crawl(base_url):
    """
    使用 Tavily 抓取整个网站内容并保存到 JSON 文件
    Crawl entire website using Tavily and save to JSON file
    """
    start_time = time.time()  # 记录开始时间
    # Record start time

    response = client.crawl(
        url=base_url,
        max_depth=2,
        extract_depth="advanced",
        format="text",
        allow_external=True,
        include_favicon=True,
    )

    end_time = time.time()  # 记录结束时间
    # Record end time
    elapsed_time = end_time - start_time  # 计算耗时
    # Calculate elapsed time
    logger.info(f"tavily_crawl 耗时: {elapsed_time:.4f} 秒")  # 打印耗时
    # Log time cost

    save_to_json(response, "tavily_crawl_test_rst.json")


def tavily_map(url):
    """
    使用 Tavily 地图扫描网站结构
    Scan website structure using Tavily map API
    """
    start_time = time.time()  # 记录开始时间
    # Record start time

    response = client.map(url=url, exclude_paths=["/private/.*", "/admin/.*"])
    print(response)

    end_time = time.time()  # 记录结束时间
    # Record end time
    elapsed_time = end_time - start_time  # 计算耗时
    # Calculate elapsed time
    logger.info(f"tavily_map 耗时: {elapsed_time:.4f} 秒")  # 打印耗时
    # Log time cost


def concurrent_task(task_func, input_list: list, concurrency: int):
    """
    通用并发执行 tavily 任务的函数。

    参数:
        task_func (function): 要并发执行的任务函数，
        input_list (list): 任务函数所需的输入参数列表，每个元素为一个参数（如搜索词或 URL）。
        concurrency (int): 并发线程数，控制同时执行的任务数量。

    ———————————————————————————————————————————————————————
    Generic function for concurrently executing Tavily tasks.

    Parameters:
        task_func (function): The function to be executed concurrently.
        input_list (list): List of input parameters for the function (e.g., search queries or URLs).
        concurrency (int): Number of threads to control parallel execution.
    """
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(task_func, item) for item in input_list]
        for future in futures:
            future.result()


def concurrent_tavily_search(questions: list, concurrency: int = 4):
    """
    并发执行 Tavily 搜索任务。

    参数:
        questions (list): 包含多个搜索关键词的列表。
        concurrency (int): 并发线程数，默认为 4。

    ———————————————————————————————————————————————————————
    Concurrently perform Tavily search tasks.

    Parameters:
        questions (list): List of search queries.
        concurrency (int): Number of concurrent threads, default is 4.
    """
    concurrent_task(tavily_search, questions, concurrency)


def concurrent_tavily_read(urls: list, concurrency: int = 4):
    """
    并发执行 Tavily 抓取网页内容任务。

    参数:
        urls (list): 包含多个目标网页地址的列表。
        concurrency (int): 并发线程数，默认为 4。

    ———————————————————————————————————————————————————————
    Concurrently extract webpage content using Tavily.

    Parameters:
        urls (list): List of target URLs.
        concurrency (int): Number of concurrent threads, default is 4.
    """
    concurrent_task(tavily_read, urls, concurrency)


def concurrent_tavily_crawl(urls: list, concurrency: int = 2):
    """
    并发执行 Tavily 网站爬取任务。

    参数:
        urls (list): 包含多个要爬取的网站根地址。
        concurrency (int): 并发线程数，默认为 2（因为 crawl 耗资源）。

    ———————————————————————————————————————————————————————
    Concurrently crawl websites using Tavily.

    Parameters:
        urls (list): List of website root URLs.
        concurrency (int): Number of concurrent threads, default is 2 due to resource usage.
    """
    concurrent_task(tavily_crawl, urls, concurrency)


def concurrent_tavily_map(urls: list, concurrency: int = 4):
    """
    并发执行 Tavily 网站地图扫描任务。

    参数:
        urls (list): 包含多个要扫描的网站根地址。
        concurrency (int): 并发线程数，默认为 4。

    ———————————————————————————————————————————————————————
    Concurrently scan website structures using Tavily map.

    Parameters:
        urls (list): List of website root URLs to scan.
        concurrency (int): Number of concurrent threads, default is 4.
    """
    concurrent_task(tavily_map, urls, concurrency)


if __name__ == "__main__":
    # 定义用于测试的问题列表
    # Define a list of questions for testing
    questions = [
        "NBA历史上得分榜排名第一的球员是谁？",
        "哪支球队赢得过最多的NBA总冠军？",
        "Who is the leading scorer in NBA history?",
        "Which team has won the most NBA championships?",
    ]

    # 定义用于测试的URL列表
    # Define a list of URLs for testing
    urls = [
        "https://www.aibase.com/zh/news/19787",
        "https://www.aibase.com/zh/news/19786",
        "https://www.aibase.com/zh/news/19785",
        "https://www.aibase.com/zh/news/19784",
    ]

    # Test website root URLs for crawling and mapping
    websites = [
        "https://www.hupu.com/",
        "https://www.zhihu.com/",
        "https://www.sohu.com/",
    ]

    # Test tavily_search function
    tavily_search(questions[0])

    # Test tavily_read function
    # tavily_read(urls)

    # Test tavily_crawl function
    # tavily_crawl(urls[0])

    # Test tavily_map function
    # tavily_map(urls[0])

    # Concurrently perform search tasks
    # concurrent_tavily_search(questions)

    # Concurrently extract webpage content
    # concurrent_tavily_read(urls)

    # Concurrently crawl websites
    # concurrent_tavily_crawl(websites)

    # Concurrently scan website maps
    # concurrent_tavily_map(websites)
