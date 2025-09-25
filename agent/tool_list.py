web_search_func = {
    "type": "function",
    "function": {
        "name": "get_websearch_result",
        "description": "Use this function to retrieve up-to-date or broad information from Google Search, especially when local data is insufficient. Suitable for querying recent news, events, people, or factual information.",
        "parameters": {
            "type": "object",
            "properties": {
                "search_query": {
                    "type": "string",
                    "description": "The query string for Google search, e.g., Who won the Turing Award in 2024. Do not use quotation marks in the search_query.",
                }
            },
            "required": ["search_query"],
        },
    },
}


search_plan_func = {
    "type": "function",
    "function": {
        "name": "get_search_plan",
        "description": "Use this function to generate a step-by-step search plan for addressing complex user queries. This is especially helpful for breaking down multi-hop or broad questions into manageable sub-queries.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_query": {
                    "type": "string",
                    "description": "The user's query, e.g., 'Summarize and analyze the 10 most important technical research achievements in the field of large language models from 2020 to the present.'",
                }
            },
            "required": ["user_query"],
        },
    },
}


def get_tool_list():
    tools = [web_search_func, search_plan_func]
    return tools
