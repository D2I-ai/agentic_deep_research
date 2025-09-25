import logging
from typing import List, Tuple

from _setting import LLM_MODEL_NAME, NUM_WEBPAGES
from agent.model import dashscope_openai_api
from agent.prompt import (
    CONTENT_SUMMARIZE_PROMPT,
    PLAN_GEN_PROMPT_V1,
    QUERY_REWRITE_PROMPT,
)
from agent.utils import get_url2favicon, get_websearch_content
from tools.log import logger_instance as logger
from websearch.query2text import query2text

# Configuration constants
QUERY_REWRITE = True
LLM_SUMMARIZATION = False


async def get_websearch_result(search_query: str) -> Tuple[str, List[str], dict]:
    """
    Perform web search and process results.

    Args:
        search_query: The original search query

    Returns:
        Tuple of (processed_content, search_queries, url_favicon_mapping)
    """
    # Generate search queries through rewriting if enabled
    if QUERY_REWRITE:
        search_queries = _rewrite_search_query(search_query)
    else:
        search_queries = [search_query]

    logger.info(f"Rewritten sub-queries: {search_queries}")

    # Perform web search
    websearch_results = await query2text(search_queries, NUM_WEBPAGES)

    # Extract content and metadata
    websearch_content = get_websearch_content(websearch_results)
    url_favicon_mapping = get_url2favicon(websearch_results)

    # Summarize content if enabled
    if LLM_SUMMARIZATION:
        try:
            websearch_content = _summarize_websearch_content(
                search_queries, websearch_content
            )
        except Exception as e:
            logger.warning(f"Content summarization failed: {e}")

    return websearch_content, search_queries, url_favicon_mapping


def get_search_plan(user_query: str) -> str:
    """
    Generate research plan based on user query.

    Args:
        user_query: The user's original research query

    Returns:
        Generated research plan as string
    """
    prompt = PLAN_GEN_PROMPT_V1.format(user_query=user_query)
    logger.debug(f"Generating research plan for query: {user_query}")
    response = dashscope_openai_api(prompt=prompt, model_name=LLM_MODEL_NAME)
    logger.info(f"The research plan has been generated as follows: {response}")

    return response


def _rewrite_search_query(original_query: str) -> List[str]:
    """
    Rewrite original query into multiple sub-queries for better search coverage.

    Args:
        original_query: The original search query

    Returns:
        List of rewritten search queries
    """
    try:
        prompt = QUERY_REWRITE_PROMPT.format(input_query=original_query)
        response = dashscope_openai_api(prompt=prompt, model_name=LLM_MODEL_NAME)

        # Safely evaluate the response as a list
        search_queries = eval(response)
        if isinstance(search_queries, list):
            logger.info(
                f"Input query was rewritten into {len(search_queries)} sub-queries"
            )
            return search_queries
        else:
            logger.warning(
                "Query rewriting returned invalid format, using original query"
            )
            return [original_query]
    except Exception as e:
        logger.error(f"Query rewriting failed, using original query: {e}")
        return [original_query]


def _summarize_websearch_content(search_queries: List[str], content: str) -> str:
    """
    Summarize web search content using LLM.

    Args:
        search_queries: List of search queries used
        content: Raw web search content to summarize

    Returns:
        Summarized content
    """
    prompt = CONTENT_SUMMARIZE_PROMPT.format(
        query=search_queries, websearch_content=content
    )
    logger.debug("Starting content summarization")
    response = dashscope_openai_api(prompt=prompt, model_name=LLM_MODEL_NAME)
    logger.debug("Content summarization completed")
    return response
