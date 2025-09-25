import asyncio
import json
import threading
from pathlib import Path

from agent.functions import get_search_plan, get_websearch_result
from agent.model import dashscope_llm_api_message, dashscope_llm_api_stream
from agent.prompt import LANG_TYPE_DESC, LLM_SUMMARIZE_PROMPT_EN_V1, SYSTEM_PROMPT_EN_V1
from agent.tool_list import get_tool_list
from agent.utils import get_trajectory, stream_generator, update_status
from tools.file_parse import handle_file_name, save2Json, save2md
from tools.lang_process import is_chinese
from tools.log import logger_instance as logger

from _setting import DEEPRESEARCH_OUTPUT_DIR, MAX_ITERATION_ROUNDS, LLM_MODEL_NAME

file_lock = threading.Lock()


class DeepResearch:
    def __init__(self, input_query: str, model: str, stream: bool = False):
        self.input_query = input_query
        self.model_name = model
        self.stream_mode = stream
        self.max_iterations = MAX_ITERATION_ROUNDS
        self.search_status = "In Progress"
        self.current_message = {}
        self.message_history = []
        self.tools = get_tool_list()
        self.final_answer = ""
        self.trajectory = ""
        self.detailed_status = {}
        self.status_log = []
        self.language_type = "en" if not is_chinese(input_query) else "zh"
        self.save_file_name = handle_file_name(input_query)
        self._initialize_messages()
        logger.info(f"Initialization done. result file name: {self.save_file_name}\n")

    def _initialize_messages(self):
        """Initialize the conversation messages with system and user prompts."""
        self.message_history = [
            {"role": "system", "content": SYSTEM_PROMPT_EN_V1},
            {"role": "user", "content": self.input_query},
        ]

    async def _process_tool_call(self):
        """Handle tool calling from LLM response."""
        tool_calls = self.current_message.get("tool_calls")
        if tool_calls:
            func_call = tool_calls[0]["function"]
            func_name = func_call.get("name", "")
            try:
                func_args = json.loads(func_call.get("arguments", "{}"))
            except json.JSONDecodeError:
                func_args = {}
                logger.warning("Failed to decode function arguments.")

            if func_name:
                await self._execute_tool(func_name, func_args)
                self.message_history.append(
                    {
                        "tool_call_id": tool_calls[0]["id"],
                        "role": "tool",
                        "name": func_name,
                        "content": self.tool_result,
                    }
                )
            else:
                self.message_history.append(
                    {
                        "tool_call_id": tool_calls[0]["id"],
                        "role": "tool",
                        "name": "",
                        "content": "",
                    }
                )
        else:
            summary_prompt = LLM_SUMMARIZE_PROMPT_EN_V1.format(
                Lang_desc=LANG_TYPE_DESC[self.language_type]
            )
            self.message_history.append({"role": "user", "content": summary_prompt})
            self.search_status = "Searching Completed"

    async def _execute_tool(self, func_name: str, func_args: dict):
        """Execute the corresponding tool based on function name."""
        if func_name == "get_search_plan":
            update_status(
                self.save_file_name,
                self.status_log,
                self.detailed_status,
                "Generating the research plan...",
                file_lock,
            )
            user_query = func_args.get("user_query")
            self.tool_result = get_search_plan(user_query)
            self.detailed_status = {"search_plan": self.tool_result}
            update_status(
                self.save_file_name,
                self.status_log,
                self.detailed_status,
                "Research plan completed.",
                file_lock,
            )

        elif func_name == "get_websearch_result":
            search_query = func_args.get("search_query")
            self.detailed_status = {"search_query": search_query}
            update_status(
                self.save_file_name,
                self.status_log,
                self.detailed_status,
                "Researching websites...",
                file_lock,
            )

            self.tool_result, web_queries, url_favicon = await get_websearch_result(
                search_query
            )
            self.detailed_status = {
                "websearch_queries": web_queries,
                "url2favicon": url_favicon,
                "websearch_content": "",
            }
            update_status(
                self.save_file_name,
                self.status_log,
                self.detailed_status,
                "Web search completed.",
                file_lock,
            )

    async def inference(self):
        """Main inference loop to interact with the LLM and process tool calls."""
        iteration = 0
        while iteration < self.max_iterations:
            update_status(
                self.save_file_name, self.status_log, {}, "Thinking...", file_lock
            )

            # logger.info(f"input prompt is:\n {self.message_history}\n\n")
            self.current_message = dashscope_llm_api_message(
                messages=self.message_history,
                tools=self.tools,
                model_name=self.model_name,
            )
            self.detailed_status = {
                "thinking_content": self.current_message.get("content", "")
            }
            update_status(
                self.save_file_name,
                self.status_log,
                self.detailed_status,
                "Thinking...",
                file_lock,
            )

            self.message_history.append(self.current_message)
            await self._process_tool_call()
            iteration += 1

            if self.search_status == "Searching Completed":
                break

        update_status(
            self.save_file_name,
            self.status_log,
            {},
            "Generating final answer...",
            file_lock,
        )

        if not self.stream_mode:
            self.current_message = dashscope_llm_api_message(
                messages=self.message_history,
                tools=self.tools,
                model_name=self.model_name,
            )
            self.message_history.append(self.current_message)
            self.final_answer = self.current_message.get("content", "")
            self.trajectory = get_trajectory(self.message_history)
            self._save_files(self.final_answer, self.trajectory)
            return self.final_answer
        else:
            self.current_message = dashscope_llm_api_stream(
                messages=self.message_history,
                tools=self.tools,
                model_name=self.model_name,
            )
            return stream_generator(self)

    def _save_files(self, final_answer, answer_trajectory):
        """Save final answer and trajectory to JSON and Markdown files."""
        try:
            save2Json(
                self.message_history,
                DEEPRESEARCH_OUTPUT_DIR / f"{self.save_file_name}.json",
            )
            save2md(final_answer, DEEPRESEARCH_OUTPUT_DIR / f"{self.save_file_name}.md")
            save2md(
                answer_trajectory,
                DEEPRESEARCH_OUTPUT_DIR / f"{self.save_file_name}-trajectory.md",
            )
        except (FileNotFoundError, PermissionError, IOError) as e:
            logger.error(f"An error occurred while saving the file: {e}")


def test_tool_calling():
    """Test function to check if tool calling is working correctly."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_EN_V1},
        {
            "role": "user",
            "content": "Purpose, Motives, and Potential International Impact of Trump's Trade War",
        },
    ]
    tools = get_tool_list()
    response = dashscope_llm_api_message(
        messages=messages, tools=tools, model_name="qwen-max-2025-01-25"
    )
    logger.info(f"Tool calling test result: {response}")


if __name__ == "__main__":
    # Uncomment to run test
    # test_tool_calling()

    # Test queries
    user_query = (
       "I have a Chinese passport and want to travel to the US, Japan, Argentina, "
       "Saudi Arabia, Thailand, and South Korea within 30 days. What is the minimal "
       "visa strategy and how should I apply for them?"
    )
    # user_query = "我拿中国护照，想用30天时间到美国、日本、阿根廷、沙特、泰国、韩国玩一圈，告诉我需要最少需要办那些签证，出一份办签证最优攻略。"
    # user_query = "国庆期间，我准备从杭州出发去云南旅游，请帮我整理一个详细的旅游攻略，涉及出行、住宿、游玩、吃饭、注意事项等，给出详细数据"

    deep_research = DeepResearch(user_query, LLM_MODEL_NAME)
    asyncio.run(deep_research.inference())
