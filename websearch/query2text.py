import asyncio
import copy
import json
import re
from collections import defaultdict
from urllib.parse import urljoin
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from gne import GeneralNewsExtractor
from readability import Document

from tools.file_parse import *
from tools.log import logger_instance as logger
from websearch.firecrawl_api import firecrawl_read_async, firecrawl_search_async
from websearch.jina_api import jina_read_async, jina_search_async
from websearch.jina_read_local_api import local_jina_read_async
from websearch.tavily_api import tavily_read_async, tavily_search_async
from websearch.utils import (
    adjust_data_format,
    filter_serpe_data,
)

from _setting import *

google_search_api = APIKeys.get("serper_api", "")


async def html2text_gne(html_content):
    """用gne提取主要内容"""
    # 使用BeautifulSoup解析HTML内容
    # Parse HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    formatted_html = soup.prettify()
    extractor = GeneralNewsExtractor()
    result = extractor.extract(
        formatted_html,
        host="https://www.xxx.com",
        # body_xpath='//div[@class="show_text"]',
        noise_node_list=[
            '//div[@class="comment-list"]',
            '//*[@style="display:none"]',
            '//div[@class="statement"]',
        ],
        use_visiable_info=False,
    )
    return result


async def html2text_rb(html, base_url):
    """用readability-lxml提取主要内容并解析网站图标"""
    try:
        doc = Document(html)
        # 需要原始HTML来解析网站图标
        # Need raw HTML to parse website favicon
        soup = BeautifulSoup(html, "lxml")

        # 提取网站图标
        # Extract website favicon
        favicon_url = ""
        common_icon = [
            "icon",
            "shortcut icon",
            "apple-touch-icon",
            "apple-touch-icon-precomposed",
        ]
        icon_link = soup.find("link", rel=lambda x: x and x.lower() in common_icon)
        if icon_link and icon_link.get("href"):
            favicon_url = icon_link["href"]
        if favicon_url and not favicon_url.startswith(("http://", "https://")):
            favicon_url = urljoin(base_url, favicon_url)

        # 提取正文内容（原逻辑）
        # Extract main content (original logic)
        summary = doc.summary()
        content_soup = BeautifulSoup(summary, "lxml")
        for tag in content_soup(
            [
                "script",
                "style",
                "nav",
                "footer",
                "aside",
                "header",
                "form",
                "button",
                "input",
                "noscript",
            ]
        ):
            tag.decompose()
        text = content_soup.get_text(separator="\n")
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[\xa0\u3000]+", " ", text).strip()

        return {"title": doc.title(), "content": text[:60000], "favicon": favicon_url}

    except Exception as e:
        print(f"解析HTML出错: {e}")
        return {"title": "", "content": "", "favicon": ""}


async def htmls2text(htmls):
    res = defaultdict(list)
    for index, (html, url, title, query) in enumerate(htmls):
        if html:
            data = await html2text_rb(html, url)
            content = data["content"]
            favicon = data["favicon"]

            if title == "":
                title = data["title"]
        else:
            content, favicon = "", ""
        query = query[0] if isinstance(query, list) else query
        res[query].append(
            {"url": url, "title": title, "favicon_url": favicon, "content": content}
        )
    # 调整返回数据格式
    # Adjust return data format
    format_res = adjust_data_format(res)
    return format_res


async def query2url(query, num_webpages):
    url = "https://google.serper.dev/search"
    params = []
    data = {
        "q": query,
        # "location": "China",
        # "gl": "cn",
        # "hl": "zh-cn",
        "num": num_webpages,
    }
    if isinstance(query, str):
        params.append(data)
    else:  # 问题列表 | Question list
        for q in query:
            param = copy.deepcopy(data)
            param["q"] = q
            params.append(param)

    payload = json.dumps(params)
    headers = {"X-API-KEY": google_search_api, "Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                url, headers=headers, data=payload, timeout=QUERY2URL_TIMEOUT
            ) as response:
                response_json = await response.json()
                return response_json
        except asyncio.TimeoutError:
            print(f"Google API请求超时: {query}")
            return []
        except Exception as e:
            print(f"Google API请求失败: {e}")
            return []


async def _fetch_search(session, url, param):
    try:
        async with session.post(
            url,
            json=param,  # 使用json参数自动序列化 | Automatically serialize parameter
            timeout=QUERY2URL_TIMEOUT,
        ) as resp:
            resp.raise_for_status()
            return await resp.json()
    except aiohttp.ClientResponseError as e:
        print(f"API错误: {e.status} {e.message}")
        return {"code": e.status, "message": str(e)}
    except Exception as e:
        print(f"请求失败: {str(e)}")
        return {"code": 500, "message": "Internal Error"}


async def fetch_html(session, url, title, query):
    headers = {
        "User-Agent": UserAgent().random,
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
    }
    try:
        # 异步获取HTML内容
        # Asynchronously fetch HTML content
        async with session.get(
            url, headers=headers, ssl=False, timeout=URL2HTML_TIMEOUT
        ) as response:
            response.raise_for_status()  # 确保请求成功 | Ensure request succeeded
            return (
                await response.text(),
                url,
                title,
                query,
            )  # 返回HTML内容及元数据 | Return HTML content and metadata
    except asyncio.TimeoutError as et:
        logger.error(f"获取html请求超时: {url}\n{et}")
        return "", url, title, query
    except Exception as e:
        logger.error(f"获取html失败： {e}")
        return (
            "",
            url,
            title,
            query,
        )  # 请求失败返回空内容 | Return empty content on failure


async def url2html(data=None, url="", query=""):
    # 控制并发数量以提高性能
    # Control concurrency to improve performance
    data = data
    connector = aiohttp.TCPConnector(limit=FETCH_HTML_CONCURRENCY_LIMIT)
    async with aiohttp.ClientSession(connector=connector) as session:
        fetch_tasks = []
        # 如果指定了url，则只处理该url
        # If URL is provided, only fetch that URL
        if url:
            fetch_tasks = [fetch_html(session, url, "", query)]
        # 否则从data中提取url列表进行批量处理
        # Otherwise, extract URLs from data and batch process
        else:
            fetch_tasks = [
                fetch_html(session, item[2], item[1], item[0]) for item in data
            ]
        # 使用asyncio.gather并发执行所有任务
        # Use asyncio.gather to execute all tasks concurrently
        html_content_list = await asyncio.gather(*fetch_tasks)

        return html_content_list


async def query2text(query, num_webpages, url="", site_search=None):
    if site_search is True and WEBSEARCH_API not in ["jina", "local_jina"]:
        logger.warning(f"{WEBSEARCH_API}不支持site_search功能，请使用local_jina或jina")
        return []

    if WEBSEARCH_API == "jina":
        if url and not site_search:
            return await jina_read_async(query, url)
        else:
            return await jina_search_async(
                query,
                search_and_read=True,
                web_site_urls=url,
                num_webpages=num_webpages,
            )
    elif WEBSEARCH_API == "local_jina":
        if url and not site_search:
            return [await local_jina_read_async(query, url)]
        else:
            res = []
            jina_search_res = await jina_search_async(
                query, web_site_urls=url, num_webpages=num_webpages
            )
            for item in jina_search_res:
                query = item["query"]
                urls = [i["url"] for i in item["results"]]
                titles = [i["title"] for i in item["results"]]
                favicon_urls = [i["favicon_url"] for i in item["results"]]
                data = await local_jina_read_async(query, urls, titles, favicon_urls)
                res.append(data)
            return res

    elif WEBSEARCH_API == "tavily":
        if url:
            return [await tavily_read_async(query, url)]
        else:
            return await tavily_search_async(query)
    elif WEBSEARCH_API == "firecrawl":
        if url:
            return [await firecrawl_read_async(query, url)]
        else:
            return await firecrawl_search_async(query)
    elif WEBSEARCH_API == "custom":
        # 用户指定URL时直接抓取页面内容
        # If URL is provided, fetch HTML directly
        if url:
            html_contents = await url2html(url=url, query=query)
        # 否则通过搜索引擎获取结果
        # Else, perform search to get URLs
        else:
            # 第1步：搜索获取相关URL
            # Step 1: Search to get relevant URLs
            serpe_data = await query2url(query, num_webpages)
            response_data = filter_serpe_data(serpe_data)
            if not response_data:
                return defaultdict(list)
            # 第2步：根据搜索结果获取HTML内容
            # Step 2: Fetch HTML content from URLs
            html_contents = await url2html(data=response_data)
        # 第3步：提取HTML中的正文内容
        # Step 3: Extract main content from HTML
        format_res = await htmls2text(html_contents)
        return format_res
    else:
        print(
            "WEBSEARCH_API config error, please use 'jina' or 'tavily' or 'firecrawl' or 'custom'"
        )
        exit()


async def main():
    # Single query test request
    # query = "Who is the Turing Award winner in 2024?"
    # res = await query2text(query, NUM_WEBPAGES)

    # Query list test request
    # query = ["Who is the Turing Award winner in 2024?", "Introduciton of GPT5"]
    # res = await query2text(query, NUM_WEBPAGES)

    # query = "Who is the Turing Award winner in 2024?"
    query = ["Who is the Turing Award winner in 2024?", "Introduciton of GPT5"]
    res = await query2text(query, NUM_WEBPAGES)

    # Save the result to a JSON file
    save2Json(res, "websearch_test_rst.json")


if __name__ == "__main__":
    asyncio.run(main())
