import json
import re
import threading
from typing import Any, Dict, Generator, List

from _setting import (
    DEFAULT_CLIP_LENGTH_CHINESE,
    DEFAULT_CLIP_LENGTH_OTHER,
    MAX_WEB_CHUNKS,
    STREAM_DELIMITER,
    THINKING_STATUS_DIR,
)
from tools.file_parse import save2Json
from tools.lang_process import is_chinese
from tools.log import logger_instance as logger

MAX_CHUNKS_PER_QUERY = 5

def clean_text(text: str) -> str:
    """
    Cleans text data scraped from frontend pages, removing invalid spaces,
    consecutive newlines, tabs, and other irrelevant content.
    """
    if not isinstance(text, str):
        logger.warning("Input to clean_text is not a string. Returning as is.")
        return text

    # 1. Replace tabs with a single space
    text = text.replace("\t", " ")
    # 2. Replace multiple spaces with a single space
    text = re.sub(r"[ ]+", " ", text)
    # 3. Replace excessive newlines and carriage returns with a single newline
    text = re.sub(r"[\r\n]+", "\n", text)
    # 4. Remove leading/trailing spaces from each line
    lines = [line.strip() for line in text.split("\n")]
    # 5. Remove empty lines
    lines = [line for line in lines if line]
    # 6. Join the cleaned lines back into a single string
    cleaned_text = "\n".join(lines)
    return cleaned_text


def get_websearch_content(websearch_results: List[Dict[str, Any]]) -> str:
    """
    Extracts and concatenates content from web search results,
    applying length limits based on language.

    Args:
        websearch_results: A list of search query results.

    Returns:
        A string containing the concatenated and clipped content.
    """
    full_content = ""
    collected_chunks = 0

    try:
        for query_item in websearch_results:
            single_query_content = ""
            collected_chunks_per_query = 0
            for result_item in query_item.get("results", []):
                if collected_chunks_per_query>=MAX_CHUNKS_PER_QUERY:
                    break
                content = result_item.get("content", "")
                if content:
                    cleaned_content = clean_text(content)
                    # Determine clip length based on language of the beginning of the content
                    clip_len = (
                        DEFAULT_CLIP_LENGTH_CHINESE
                        if is_chinese(cleaned_content[:10])
                        else DEFAULT_CLIP_LENGTH_OTHER
                    )

                    single_query_content += cleaned_content[:clip_len] + "\n\n"
                    collected_chunks_per_query += 1
                    collected_chunks += 1

                    if collected_chunks >= MAX_WEB_CHUNKS:
                        logger.info(
                            f"Reached maximum web chunks ({MAX_WEB_CHUNKS}). Stopping content collection."
                        )
                        break
            full_content += single_query_content
            if collected_chunks >= MAX_WEB_CHUNKS:
                break
    except Exception as e:
        logger.error(f"Error extracting websearch content: {e}", exc_info=True)
        # Return partial content if possible
    return full_content


def get_url2favicon(websearch_results: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Extracts a mapping of URLs to their corresponding favicon URLs from search results.

    Args:
        websearch_results: A list of search query results.

    Returns:
        A dictionary mapping URLs to favicon URLs.
    """
    url_to_favicon = {}
    try:
        for query_result in websearch_results:
            for search_result in query_result.get("results", []):
                url = search_result.get("url")
                favicon_url = search_result.get("favicon_url")
                if url and favicon_url:  # Ensure both keys exist and have values
                    url_to_favicon[url] = favicon_url
    except Exception as e:
        logger.error(f"Error extracting URL to favicon map: {e}", exc_info=True)
    return url_to_favicon


def get_trajectory(message_list: List[Dict[str, Any]]) -> str:
    """
    Extracts and formats a trajectory of the conversation from the message history.

    Args:
        message_list: A list of message dictionaries from the LLM interaction.

    Returns:
        A formatted string representing the conversation trajectory.
    """
    answer_trajectory = ""
    try:
        for index, item in enumerate(message_list):
            role = item.get("role")
            content = item.get("content", "")

            if index == 1 and role == "user":
                answer_trajectory += f"<user_query>{content}</user_query>\n"
            elif role == "assistant" and item.get("tool_calls") is not None:
                if content:
                    answer_trajectory += f"<thinking>{content}</thinking>\n"
                tool_call = item.get("tool_calls", [{}])[0]
                function_name = tool_call.get("function", {}).get("name")
                if function_name == "get_websearch_result":
                    arguments_str = tool_call.get("function", {}).get("arguments", "{}")
                    try:
                        arguments = json.loads(arguments_str)
                        search_query = arguments.get("search_query", "")
                        answer_trajectory += f"<search>{search_query}</search>\n"
                    except json.JSONDecodeError:
                        logger.warning(
                            f"Could not decode arguments for tool call: {arguments_str}"
                        )
            elif role == "tool" and content:
                tool_name = item.get("name", "")
                if tool_name == "get_search_plan":
                    answer_trajectory += f"<plan>{content}</plan>\n"
                else:
                    answer_trajectory += f"<information>{content}</information>\n"
            elif role == "assistant" and item.get("tool_calls") is None:
                if index < len(message_list) - 1 and content:
                    answer_trajectory += f"<thinking>{content}</thinking>\n"
                elif index == len(message_list) - 1:  # Final answer
                    answer_trajectory += f"<answer>{content}</answer>"
    except Exception as e:
        logger.error(f"Error generating trajectory from messages: {e}", exc_info=True)
        # Return partial trajectory if possible
    return answer_trajectory


def update_status(
    save_file_name: str,
    status_list: List[Dict[str, Any]],
    detailed_status: Dict[str, Any],
    status_description: str,
    file_lock: threading.Lock,  # Assuming threading.Lock is imported or passed correctly
) -> None:
    """
    Updates the status of an agent's process and saves it to a JSON file.

    Args:
        save_file_name: The base name for the status file (without extension).
        status_list: The list of status dictionaries to append to.
        detailed_status: A dictionary containing detailed status information.
        status_description: A brief description of the current status.
        file_lock: A threading lock to ensure thread-safe file writing.
    """
    try:
        current_status = {
            "status_desc": status_description,
            "detailed_status": detailed_status,
        }

        status_list.append(current_status)
        status_file_path = THINKING_STATUS_DIR / f"{save_file_name}.json"

        with file_lock:
            save2Json(status_list, str(status_file_path))
        logger.debug(f"Updated status for {save_file_name}")
    except Exception as e:
        logger.error(
            f"Failed to update status for {save_file_name}: {e}", exc_info=True
        )


def stream_generator(self) -> Generator[str, None, None]:
    """
    Generator function to yield streamed LLM responses and handle finalization.

    Args:
        self: The instance of the class (e.g., DeepResearch) that holds the stream context.

    Yields:
        str: Formatted JSON strings representing the stream chunks or final status.
    """
    if not self.stream_mode:
        logger.warning("stream_generator called but stream_mode is False.")
        return

    final_answer = ""
    is_first_token = True

    try:
        for (
            token_chunk
        ) in (
            self.current_message
        ):  # Assuming self.current_message is the stream generator
            # Build the incremental response object
            response_chunk = {
                "status": "generating",
                "record_id": "",
                "increase": False,
                "output": token_chunk,
            }

            # Add context for the first token
            if is_first_token:
                response_chunk.update(
                    {
                        "input": self.input_query,
                        "output": token_chunk,  # Overwrites previous output, which is fine
                        "status": "generating",
                        "record_id": "",
                        "context": "",  # Assuming context is empty initially
                    }
                )
                is_first_token = False

            # Yield the formatted chunk
            yield json.dumps(response_chunk, ensure_ascii=False) + STREAM_DELIMITER
            final_answer += str(token_chunk)  # Accumulate the full answer

        # Signal the end of the stream
        yield json.dumps(
            {"status": "stop", "record_id": "", "increase": False, "output": ""},
            ensure_ascii=False,
        )

        # Finalize: Append the full answer to message history
        self.message_history.append(
            {
                "content": final_answer,
                "refusal": None,
                "role": "assistant",
                "annotations": None,
                "audio": None,
                "function_call": None,
                "tool_calls": None,
            }
        )

        # Generate and save the final trajectory and answer
        answer_trajectory = get_trajectory(self.message_history)
        # Assuming self.save_file exists and handles saving
        self._save_files(final_answer, answer_trajectory)
        logger.debug("Stream processing completed and files saved.")

    except Exception as e:
        logger.error(f"Error during stream generation: {e}", exc_info=True)
        # Optionally yield an error message to the client
        yield json.dumps(
            {
                "status": "error",
                "record_id": "",
                "increase": False,
                "output": "An error occurred during streaming.",
            },
            ensure_ascii=False,
        )
