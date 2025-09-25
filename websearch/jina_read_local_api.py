import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

import aiohttp
import requests
from aiohttp import ClientTimeout

from _setting import *
from tools.log import logger_instance as logger
from websearch.utils import local_jina_read_response_parse, save_to_json

base_url = URLs["local_jina_read_url"]


async def jina_read_request(session, url: str, query: str, timeout=10):
    """
    Helper function to handle a single URL request.
    """
    full_url = base_url + url
    headers = {"X-Return-Format": "text", "X-Md-Link-Style": "discarded"}

    try:
        async with session.get(full_url, headers=headers, timeout=timeout) as response:
            if response.status == 200:
                content = await response.text()
                return content
            else:
                error_text = await response.text()
                logger.debug(
                    f"[{query}] Request failed | URL: {url} | "
                    f"Status code: {response.status} | "
                    f"Response: {error_text[:200]}"
                )
                return ""
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        # logger.error(f"[{query}] Request exception | URL: {url} | Error: {str(e)}")
        return ""


async def local_jina_read_async(query, url, title="", favicon_url=""):
    """
    Asynchronously process multiple URL requests.
    """
    # start_time = time.monotonic()

    url_list = url if isinstance(url, list) else [url]
    title_list = title if isinstance(title, list) else [title] * len(url_list)
    favicon_list = (
        favicon_url if isinstance(favicon_url, list) else [favicon_url] * len(url_list)
    )

    timeout = ClientTimeout(total=None)
    connector = aiohttp.TCPConnector(limit=FETCH_HTML_CONCURRENCY_LIMIT)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = []
        for idx, url in enumerate(url_list):
            tasks.append(jina_read_request(session, url, query))
        responses = await asyncio.gather(*tasks)
    res = local_jina_read_response_parse(
        query, url_list, title_list, favicon_list, responses
    )

    # elapsed_time = time.monotonic() - start_time
    # logger.info(f"[{query}] local_jina_read_async took: {elapsed_time:.4f} seconds")
    # print(f"[{query}] local_jina_read_async took: {elapsed_time:.4f} seconds")

    return res


def local_jina_read(parse_url):
    """
    Perform a single URL request to the Jina API and return the elapsed time.
    If the request fails, return None or "timeout" accordingly.
    """
    url = base_url + parse_url
    headers = {"X-Respond-With": "markdown"}  # Request response in markdown format

    try:
        # Send a GET request to the specified URL with a timeout of 100 seconds
        response = requests.get(url, headers=headers, timeout=100)

        if response.status_code == 200:

            res_item = {"url": parse_url, "content": response.text}
            res = {"query": "", "results": res_item}

            return res

        else:
            # Log an error message if the request fails with a non-200 status code
            print(f"Request failed, status code: {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        # Handle timeout exceptions
        print(f"Request timed out: {url}")
        return "timeout"
    except Exception as e:
        # Handle other exceptions
        print(f"Request encountered an exception: {str(e)}")
        return None


def concurrent_local_read(urls, concurrency):

    res = []
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(local_jina_read, url) for url in urls]
        for future in futures:
            data = future.result()
            res.append(data)
    return res


def test_concurrent_local_read(urls, concurrency, batch=0):
    # 使用线程池执行器进行并发请求
    # Use ThreadPoolExecutor for concurrent requests

    start_time = time.time()
    res = concurrent_local_read(urls, concurrency)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Complete jina read in: {elapsed_time:.4f} seconds")

    save_to_json(res, f"concurrent_local_read_test_rst_{batch}.json")


def test_local_jina_read(urls):
    """
    Test the local_jina_read function with a list of URLs and calculate statistics.
    """
    res = []

    for i, url in enumerate(urls, 1):
        print(f"Read URL {i}: {url}")  # Log the current URL being tested
        data = local_jina_read(url)
        res.append(data)

    save_to_json(res, "local_jina_read_test_rst.json")


if __name__ == "__main__":

    # Test cases for URL list
    test_query = "test_query"

    test_urls = [
        "https://www.aibase.com/zh/news/19787",
        "https://www.aibase.com/zh/news/19786",
    ] * 10

    # local jina read service test
    # test_local_jina_read(test_urls)

    # concurrent test
    # test_concurrent_local_read(test_urls, 10)

    # async test
    ready_data_list = asyncio.run(local_jina_read_async(test_query, test_urls))
    print(ready_data_list)
