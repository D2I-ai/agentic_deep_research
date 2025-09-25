import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor

import aiohttp
import requests
from aiohttp import ClientTimeout

from _setting import *
from tools.log import logger_instance as logger
from websearch.utils import (
    jina_read_response_parse,
    jina_search_response_parse,
    merge_final_data,
    save_to_json,
)


async def jina_search_request(session, headers, query, timeout=20):
    url = "https://s.jina.ai"
    params = {"q": query}
    try:
        # 异步发送GET请求
        # Asynchronously send a GET request
        async with session.get(
            url,
            headers=headers,
            params=params,
            timeout=timeout,  # 设置超时时间 | Set timeout duration
        ) as response:
            # 检查HTTP状态码
            # Check HTTP status code
            if response.status == 200:
                res = (
                    await response.json()
                )  # 异步读取JSON响应 | Asynchronously read JSON response

                data = res["data"]
                ready_data = jina_search_response_parse(data)
                # save_to_json(ready_data, "jina_search_test_rst.json")
                return ready_data
            else:
                logger.error(f"{query} request failed，status code: {response.status}")
                return []

    except aiohttp.ClientError as e:
        logger.error(f"{query} request error: {str(e)}")
        return []
    except asyncio.TimeoutError:
        logger.error(f"{query} request timeout")
        return []


async def jina_read_request(session, url, query, headers):
    full_url = f"https://r.jina.ai/{url}"
    try:
        async with session.get(full_url, headers=headers) as response:
            # 检查响应状态
            # Check response status
            if response.status == 200:
                res = await response.json()
                data = res.get("data", {})
                # 解析响应数据
                # Parse response data
                ready_data = jina_read_response_parse(data, query)
                return ready_data
            else:
                # 记录错误详情
                # Record error details
                error_text = await response.text()
                logger.error(
                    f"request failed | URL: {url} | "
                    f"status code: {response.status} | "
                    f"response: {error_text[:200]}"
                )
                return None

    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.error(f"request exception | URL: {url} | error: {str(e)}")
        return None


async def jina_search_async(
    query,
    search_and_read=False,
    parse_favicons=True,
    web_site_urls=None,
    num_webpages=10,
):
    auth = "Bearer " + APIKeys["jina_api_key"]
    # 统一参数类型处理
    # Uniform parameter type handling
    queries = [query] if isinstance(query, str) else query
    if not web_site_urls:
        web_site_urls = []
    elif isinstance(web_site_urls, str):
        web_site_urls = [web_site_urls]
    else:
        web_site_urls = web_site_urls

    headers = {
        "Authorization": auth,
        "X-No-Cache": "true",
        "Accept": "application/json",
        "X-Return-Format": "text",
    }

    # 根据参数动态设置请求头
    # Dynamically set request headers based on parameters
    if search_and_read:
        print("DO NOT use <search_and_read=True>, because it is so expensive")
        exit()
        # headers['X-Engine'] = 'direct' # uncomment to set search_and_read=True
    else:
        headers["X-Respond-With"] = "no-content"

    if parse_favicons:
        headers["X-With-Favicons"] = "true"

    connector = aiohttp.TCPConnector(limit=FETCH_HTML_CONCURRENCY_LIMIT)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for q in queries:
            if web_site_urls:
                for web_url in web_site_urls:
                    request_headers = headers.copy()
                    request_headers["X-Site"] = web_url
                    tasks.append(jina_search_request(session, request_headers, q))
            else:
                tasks.append(jina_search_request(session, headers, q))

        task_res = await asyncio.gather(*tasks)
    res = merge_final_data(queries, task_res, web_site_urls, num_webpages)
    return res


async def jina_read_async(query, url):
    urls = url if isinstance(url, list) else [url]
    # 设置请求头
    # Set request headers
    auth = "Bearer " + APIKeys["jina_api_key"]
    headers = {
        "Authorization": auth,
        "Accept": "application/json",
        "X-No-Cache": "true",
        "X-Return-Format": "text",
        "X-Token-Budget": "30000",
    }
    timeout = ClientTimeout(total=None)
    connector = aiohttp.TCPConnector(limit=FETCH_HTML_CONCURRENCY_LIMIT)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [jina_read_request(session, url, query, headers) for url in urls]
        task_res = await asyncio.gather(*tasks)
    return task_res


def jina_read(url):
    url = "https://r.jina.ai/" + url
    auth = "Bearer " + APIKeys["jina_api_key"]
    headers = {
        "Authorization": auth,
        "Accept": "application/json",
        "X-No-Cache": "true",
        "X-Return-Format": "text",
        "X-Token-Budget": "30000",
    }

    response = requests.get(url, headers=headers)

    # 检查响应状态码
    # Check response status code
    if response.status_code == 200:
        res = response.json()
        data = res["data"]
        ready_data = jina_read_response_parse(data)

        # save_to_json(ready_data, "jina_read_test_rst.json")
        return ready_data
    else:
        logger.error(f"request failed: {response.status_code}")
        return None


def jina_search(query, search_and_read=False, parse_favicons=True, web_site_url=None):
    url = "https://s.jina.ai"
    auth = "Bearer " + APIKeys["jina_api_key"]
    headers = {
        "Authorization": auth,
        "X-No-Cache": "true",
        "Accept": "application/json",
        "X-Return-Format": "text",  # 获取内容全文,不带页面中的跳转url | Get content without redirect URLs
        "X-Respond-With": "no-content",  # 获取内容简单描述 | Get simple content description
        # "X-With-Favicons": 'true',
        # "X-Timeout": 10,  # 配置超时时间 | Configure timeout duration
    }
    if search_and_read:
        print("DO NOT use <search_and_read=True>, because it is so expensive")
        exit()
        # headers['X-Engine'] = 'direct' # uncomment to set search_and_read=True
    else:
        headers["X-Respond-With"] = "no-content"
    if parse_favicons:
        headers["X-With-Favicons"] = "true"
    if web_site_url:
        headers["X-Site"] = web_site_url
    params = {"q": query}

    response = requests.get(url, headers=headers, params=params)

    # Check response status code
    if response.status_code == 200:
        res = response.json()
        data = res["data"]
        parse_data = jina_search_response_parse(data)
        ready_data = {"query": query, "results": parse_data}
        # save_to_json(ready_data, "jina_search_test_rst.json")
        return ready_data

    else:
        logger.error(f"request failed: {response.status_code}")
        return None


def test_jina_read(urls):
    res = []
    for i, question in enumerate(urls, 1):
        print(f"read url {i}: {question}")
        data = jina_read(question)
        res.append(data)
    save_to_json(res, "jina_read_test_rst.json")


def test_jina_search(
    questions, search_and_read=False, parse_favicons=True, web_site_url=None
):
    res = []
    for i, question in enumerate(questions, 1):
        print(f"search question {i}: {question}")
        data = jina_search(question, search_and_read, parse_favicons, web_site_url)
        res.append(data)

    save_to_json(res, "jina_search_test_rst.json")


def concurrent_read(urls, concurrency, batch=0):
    # 使用线程池执行器进行并发请求
    # Use ThreadPoolExecutor for concurrent requests
    res = []
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(jina_read, question) for question in urls]
        for future in futures:
            data = future.result()
            res.append(data)
    save_to_json(res, f"jina_read_concurrent_test_rst_{batch}.json")


def concurrent_search(
    questions,
    concurrency,
    search_and_read=False,
    parse_favicons=True,
    web_site_url=None,
    batch=0,
):
    res = []
    # 使用线程池执行器进行并发搜索
    # Use ThreadPoolExecutor for concurrent search
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [
            executor.submit(
                jina_search, question, search_and_read, parse_favicons, web_site_url
            )
            for question in questions
        ]
        for future in futures:
            data = future.result()
            res.append(data)
    save_to_json(res, f"jina_search_concurrent_test_rst_{batch}.json")


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

    # jina_read test
    # test_jina_read(urls)

    # jina_search test
    # test_jina_search(questions)

    # jina_read concurrent test examples
    # concurrent_read(urls, 10)

    # jina_search concurrent test examples
    # concurrent_search(questions, 10)

    # jina_search_async test
    res = asyncio.run(jina_search_async(questions))
    print(res)
