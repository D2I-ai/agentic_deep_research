# summarize the websearch content
CONTENT_SUMMARIZE_PROMPT = """
## Task
You are an expert in information summarization. Given a user's search query and a list of retrieved text snippets from the web, you need to carefully review the content of each snippet and consolidate relevant information into key points.

## Answering Guidelines
1. Carefully evaluate the relevance of each snippet to the user's query. If a snippet does not contain information related to the query, there is no need to include it in the summary.
2. If you identify any severe factual errors in the provided content, you can ignore that incorrect information.
3. Provide a comprehensive summary of all information relevant to the user query, strictly avoiding adding any information not mentioned in the snippets.
4. Present the consolidated output in a clear and organized format. Ensure it is easy to read, with all key points systematically listed.
5. Keep the output well structured and informative, ensuring the total word count does not exceed 2000 words.

## User Query:
{query}

## Retrieved Web Content:
{content_list}

## Summarized Content
Please adhere to the above instructions to consolidate relevant information and generate a well-structured summary of key points related to the user's query, matching the language of the retrieved snippets.
"""


LLM_ANSWER_PROMPT = """\
## Task
You're a **question-answering assistant**. Your goal is to answer a user's **Query** using the provided **Reference Knowledge**.

## Guidelines
* **Summarize** your answer based on both the user's query and the provided knowledge.
* If the **Reference Knowledge is limited**, you may use your **general knowledge** to supplement the answer, but make sure it doesn't contradict the given information.
* Only provide the answer to the user's question; **do not add extra explanations or conversational fillers.**
* Ensure the output language matches the input language.
## Output
### User Query:
{query}

### Reference Knowledge:
{knowledge}

### Answer:
"""


## rewrite the search query
QUERY_REWRITE_PROMPT = """\
## Instruction
We are conducting query search on the internet to gather comprehensive information to answer the user query. Please generate up to 4 search queries for google search based on the user question.

## Guidelines
1. Make the search queries concise and specific enough to find high-quality and relevant web sources.
2. If the user query is concise and specific enough, only output the original query.
3. If the input query is in English, ensure that the rewritten sub-queries are also in English. If the input query is in Chinese, provide the rewritten sub-queries in both Chinese and English.
4. Respond exclusively in List of str format without any other text.

## Demonstration
### Input Query
图灵奖的评选标准和评选流程
### Rewritten Query
["图灵奖 评选标准", "图灵奖 评选流程", "Turing Award, Selection Criteria", "Turing Award, Selection Process"]
### Input Query
北京奥运会开幕式时间及地点
### Rewritten Query
["北京奥运会 开幕式时间", "北京奥运会开幕式地点", "Beijing Olympics, Opening Ceremony"]
### Input Query
men's 100m record
### Rewritten Query
["men's 100m record"]
### Input Query
Kobe Bean Bryant Year-of-Birth
### Rewritten Query
["Kobe Bean Bryant Year-of-Birth"]

## Output
### Input Query
{input_query}
### Rewritten Query
"""
