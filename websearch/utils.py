import json
from typing import List
from pydantic import BaseModel, Field

from _setting import NUM_WEBPAGES
from tools.log import logger_instance as logger


class HistoryItem(BaseModel):
    user: str  # 用户输入内容，必填 | Required field: user input content
    bot: str  # 系统回复内容，必填 | Required field: system response content


class WebsearchItem(BaseModel):
    input: str  # 必填字段，类型为字符串 | Required field: input query string
    url: str | list[str] | None = (
        None  # 可选字段，指定URL | Optional field: specific URL to fetch
    )
    search_count: int | None = (
        NUM_WEBPAGES  # 可选字段，搜索结果数量 | Optional field: number of search results
    )
    query_rewrite: bool | None = (
        True  # 是否重写查询语句 | Optional field: whether to rewrite query
    )
    history: List[HistoryItem] = Field(
        default_factory=list
    )  # 允许不传或为空列表 | Optional field: conversation history
    stream: bool | None = (
        False  # 是否流式输出 | Optional field: enable streaming output
    )
    # increase: bool | None = False  # 可选字段（当前注释未启用）| Optional field (currently commented out)
    site_search: bool | None = (
        None  # 是否进行站点搜索 | Optional field: whether to perform site search
    )


def filter_serpe_data(serpe_data):
    res = []
    for res_item in serpe_data:
        query = res_item["searchParameters"]["q"]
        organic_list = res_item["organic"]
        for (
            organic_item
        ) in organic_list:  # 遍历自然搜索结果 | Iterate over organic results
            title, link = organic_item["title"], organic_item["link"]
            res.append([query, title, link])
    return res


def filter_ali_search_response(ali_search_response):
    """
    过滤阿里搜索接口返回结果，提取查询语句、标题和链接
    Filter ali search response to extract query, title and link
    """
    res = []
    for res_item in ali_search_response:
        if not res_item.get("success", False):
            logger.error(f"res_item['success'] 为False: {res_item}")
            continue
        data = res_item.get("data", {})  # 获取data字段 | Get 'data' field
        if not data:
            logger.error(f"res_item 中没有data: {res_item}")
            continue
        original_output = data.get(
            "originalOutput", {}
        )  # 获取原始输出 | Get raw output
        if not original_output:
            logger.error(f"res_item['data'] 中没有originalOutput: {res_item}")
            continue
        search_parameters = original_output["searchParameters"]
        query = search_parameters["q"]  # 提取查询语句 | Extract search query
        for organic_item in original_output[
            "organic"
        ]:  # 遍历自然搜索结果 | Iterate over organic results
            title, link = organic_item["title"], organic_item["link"]
            res.append([query, title, link])
    return res


def adjust_data_format(data):
    """
    将原始数据格式转换为标准输出格式
    Convert raw data format to standard output format
    """
    res = []
    for query, items in data.items():
        query_data = dict()
        query_data["query"] = query  # 设置查询语句 | Set query field
        query_data["results"] = []
        for item in items:  # 添加每个查询结果 | Append each result
            query_data["results"].append(item)
        res.append(query_data)
    return res


def jina_search_response_parse(data):
    """
    解析 Jina 搜索接口返回的数据
    Parse Jina search response data
    """
    res = []
    for item in data:
        res_item = dict()
        res_item["url"] = item.get("url", "")  # 提取URL | Extract URL
        res_item["title"] = item.get("title", "")  # 提取标题 | Extract title

        favicon_url = item.get("favicon", "")  # 提取网站图标 | Extract favicon
        if favicon_url:
            res_item["favicon_url"] = favicon_url
        else:
            favicon_item = item.get("external", {}).get("icon", {})
            if not favicon_item:
                favicon_item = item.get("external", {}).get("apple-touch-icon", {})
            if not favicon_item:
                favicon_item = item.get("external", {}).get("mask-icon", {})
            favicon_url = list(favicon_item.keys())[0] if favicon_item else ""
            res_item["favicon_url"] = favicon_url

        res_item["content"] = item.get(
            "text", ""
        )  # 提取内容摘要 | Extract content summary
        res.append(res_item)
    return res


def local_jina_read_response_parse(query, urls, titles, favicons, contents):
    res = {"query": query, "results": []}
    for idx, url in enumerate(urls):
        title = titles[idx]
        favicon = favicons[idx]
        content = contents[idx]
        res_item = {
            "url": url,
            "title": title,
            "favicon_url": favicon,
            "content": content,
        }
        res["results"].append(res_item)
    return res


def jina_read_response_parse(item, query=""):
    """
    解析 Jina 读取网页内容接口返回的数据
    Parse Jina read response data
    """
    res_item = dict()
    res_item["url"] = item.get("url", "")  # 提取URL | Extract URL
    res_item["title"] = item.get("title", "")  # 提取标题 | Extract title

    favicon_item = item.get("external", {}).get("icon", {})
    if not favicon_item:
        favicon_item = item.get("external", {}).get("apple-touch-icon", {})
    if not favicon_item:
        favicon_item = item.get("external", {}).get("mask-icon", {})
    favicon_url = list(favicon_item.keys())[0] if favicon_item else ""
    res_item["favicon_url"] = favicon_url  # 提取网站图标 | Extract favicon

    res_item["content"] = item.get("text", "")  # 提取网页内容 | Extract page content
    res = {"query": query, "results": [res_item]}  # 组装结果 | Assemble result
    return res


def merge_final_data(queries, data, web_site_urls=None, num_webpages=10):
    """
    合并查询与对应结果
    Merge queries and their corresponding results
    """
    if web_site_urls is None:
        web_site_urls = []
    q_slice = num_webpages // len(web_site_urls) if web_site_urls else num_webpages
    res = []
    idx = 0
    for query in queries:
        if web_site_urls:
            q_result = []
            for web_site_url in web_site_urls:
                q_result.extend(data[idx][:q_slice])
                idx += 1
        else:
            q_result = data[idx][:q_slice]
            idx += 1
        res.append({"query": query, "results": q_result})
    return res


def tavily_search_response_parse(data):
    """
    解析 Tavily 搜索接口返回的数据
    Parse Tavily search response data
    """
    res = []
    for item in data:
        res_item = dict()
        res_item["url"] = item["url"]  # 提取URL | Extract URL
        res_item["title"] = item["title"]  # 提取标题 | Extract title
        res_item["favicon_url"] = item.get("favicon", "")  # 提取图标 | Extract favicon
        res_item["content"] = item["raw_content"]  # 提取内容 | Extract content
        res.append(res_item)
    return res


def tavily_read_response_parse(data, query=""):
    """
    解析 Tavily 网页内容接口返回的数据
    Parse Tavily read response data
    """
    res = {"query": query, "results": []}
    for item in data:
        res_item = dict()
        res_item["url"] = item["url"]  # 提取URL | Extract URL
        res_item["title"] = item.get("title", "")  # 提取标题 | Extract title
        res_item["favicon_url"] = item.get("favicon", "")  # 提取图标 | Extract favicon
        res_item["content"] = item["raw_content"]  # 提取网页内容 | Extract page content
        res["results"].append(res_item)
    return res


def save_to_json(data, filename):
    """
    将数据保存为 JSON 文件
    Save data to JSON file
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)  # 写入文件 | Write to file


def firecrawl_read_response_parse(item, query=""):
    """
    解析 Firecrawl 读取网页内容接口返回的数据
    Parse Firecrawl read response data
    """
    res_item = dict()
    res_item["url"] = item["metadata"]["url"]  # 提取URL | Extract URL
    res_item["title"] = item["metadata"]["title"]  # 提取标题 | Extract title
    res_item["favicon_url"] = ""  # Firecrawl 不返回图标 | Favicon not available
    res_item["content"] = item[
        "markdown"
    ]  # 提取Markdown内容 | Extract markdown content
    res = {"query": query, "results": [res_item]}  # 组装结果 | Assemble result
    return res


def firecrawl_search_response_parse(data):
    """
    解析 Firecrawl 搜索接口返回的数据
    Parse Firecrawl search response data
    """
    res = []
    for item in data:
        res_item = dict()
        res_item["url"] = item["url"]  # 提取URL | Extract URL
        res_item["title"] = item["title"]  # 提取标题 | Extract title
        res_item["favicon_url"] = item.get("favicon", "")  # 提取图标 | Extract favicon
        res_item["content"] = item["description"]  # 提取描述内容 | Extract description
        res.append(res_item)
    return res
