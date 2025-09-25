import json
import time
from http import HTTPStatus

import dashscope
from openai import APIError, APITimeoutError, OpenAI, RateLimitError

from _setting import APIKeys
from tools.log import logger_instance as logger

# --- Configuration ---
DASHSCOPE_API_KEY = APIKeys.get("dashscope_api_key", "")
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_DASHSCOPE_MODEL = "qwen-max-2025-01-25"

# --- Helper Functions ---


def _create_openai_client(api_key: str, base_url: str) -> OpenAI:
    """Creates an OpenAI client with the given API key and base URL."""
    return OpenAI(api_key=api_key, base_url=base_url)


def _handle_retry_logic(
    e: Exception, attempt: int, max_retries: int, sleep_time: float, model_name: str
):
    """Handles logging and sleeping for retry logic."""
    if isinstance(e, (APITimeoutError, RateLimitError)):
        logger.warning(
            f"Temporary error with model '{model_name}': {e}. Retrying in {sleep_time}s..."
        )
    else:
        logger.error(
            f"An error occurred with model '{model_name}' on attempt {attempt}: {e}"
        )

    if attempt < max_retries:
        time.sleep(sleep_time)
    else:
        logger.error("Max retries reached. Operation failed.")


# --- Dashscope API Functions ---
# Description https://help.aliyun.com/zh/model-studio/compatibility-of-openai-with-dashscope


def dashscope_llm_api_message(
    messages: list,
    tools: list,
    model_name: str,
    max_retries: int = 10,
    temperature: float = 0.01,
):
    """
    Calls the Dashscope API using the chat completions endpoint with message history and tools.

    Args:
        messages (list): A list of message dictionaries.
        tools (list): A list of tool definitions.
        model_name (str): The name of the model to use.
        max_retries (int): Maximum number of retry attempts.
        temperature (float): Sampling temperature.

    Returns:
        dict or None: The parsed message dictionary from the API response, or None on failure.
    """
    client = _create_openai_client(DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL)
    retries = 0
    sleep_time = 1

    while retries < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model_name if model_name else DEFAULT_DASHSCOPE_MODEL,
                messages=messages,
                tools=tools,
                temperature=temperature,
                extra_body={"enable_thinking": False},
                timeout=500,
            )
            message = completion.choices[0].message

            # Safely serialize and deserialize to ensure correct encoding
            message_json_str = message.model_dump_json()
            message_dict = json.loads(message_json_str)
            output_message = json.loads(json.dumps(message_dict, ensure_ascii=False))

            logger.debug(f"Successfully called Dashscope model '{model_name}'.")
            return output_message

        except (APIError, APITimeoutError, RateLimitError) as e:
            _handle_retry_logic(e, retries + 1, max_retries, sleep_time, model_name)
            retries += 1
        except Exception as e:
            logger.critical(
                f"Unexpected error calling Dashscope model '{model_name}': {e}",
                exc_info=True,
            )
            return None

    logger.error(
        f"Failed to call Dashscope model '{model_name}' after {max_retries} attempts."
    )
    return None


def dashscope_llm_api_stream(
    messages: list,
    tools: list,
    model_name: str,
    max_retries: int = 10,
    temperature: float = 0.01,
):
    """
    Calls the Dashscope API for streaming chat completions.

    Args:
        messages (list): A list of message dictionaries.
        tools (list): A list of tool definitions.
        model_name (str): The name of the model to use.
        max_retries (int): Maximum number of retry attempts.
        temperature (float): Sampling temperature.

    Yields:
        str or None: Chunks of content from the stream, or None on failure.
    """
    client = _create_openai_client(DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL)
    retries = 0
    sleep_time = 1

    while retries <= max_retries:
        try:
            completion = client.chat.completions.create(
                model=model_name if model_name else DEFAULT_DASHSCOPE_MODEL,
                messages=messages,
                temperature=temperature,
                tools=tools,
                stream=True,
                # stream_options={"include_usage": True},
            )

            logger.debug(f"Started streaming from Dashscope model '{model_name}'.")
            for chunk in completion:
                delta_content = (
                    chunk.choices[0].delta.content if chunk.choices else None
                )
                yield delta_content

            # If the loop completes without error, break out of retry loop
            logger.debug(
                f"Streaming from Dashscope model '{model_name}' completed successfully."
            )
            break

        except (APIError, APITimeoutError, RateLimitError) as e:
            _handle_retry_logic(e, retries + 1, max_retries, sleep_time, model_name)
            retries += 1
        except Exception as e:
            logger.critical(
                f"Unexpected error during Dashscope streaming for model '{model_name}': {e}",
                exc_info=True,
            )
            yield None
            break  # Break on unexpected error during streaming

    if retries > max_retries:
        logger.error(
            f"Failed to stream from Dashscope model '{model_name}' after {max_retries} attempts."
        )
        yield None


def dashscope_llm_api(
    prompt: str,
    model_name: str = "",
    max_retries: int = 10,
    temperature: float = 0.01,
):
    """
    Calls the Dashscope API using the legacy Generation endpoint with a simple prompt.

    Args:
        prompt (str): The text prompt for the model.
        model_name (str): The name of the model to use.
        max_retries (int): Maximum number of retry attempts.
        temperature (float): Sampling temperature.

    Returns:
        str or None: The generated text, or None on failure.
    """
    retries = 0
    sleep_time = 1

    while retries < max_retries:
        try:
            response = dashscope.Generation.call(
                model=model_name if model_name else DEFAULT_DASHSCOPE_MODEL,
                prompt=prompt,
                temperature=temperature,
                api_key=DASHSCOPE_API_KEY,
                # enable_thinking=False,
                extra_body={"enable_thinking": False},
            )
            if response.status_code == HTTPStatus.OK:
                logger.debug(
                    f"Successfully called Dashscope model '{model_name}' with prompt."
                )
                return response.output["text"]
            else:
                logger.warning(
                    f"Dashscope API returned status {response.status_code}: {response}"
                )
                time.sleep(sleep_time)
                retries += 1
                logger.info(
                    f"Retrying in {sleep_time} seconds... (Attempt {retries} of {max_retries})"
                )

        except Exception as e:
            logger.error(
                f"An error occurred calling Dashscope model '{model_name}' with prompt: {e}"
            )
            retries += 1
            if retries < max_retries:
                time.sleep(sleep_time)
            else:
                logger.error(
                    "Max retries reached for prompt-based call. Returning None."
                )
                return None
    return None


def dashscope_openai_api(
    prompt: str,
    model_name: str = "",
    max_retries: int = 10,
    temperature: float = 0.01,
):
    """
    Calls the Dashscope API using the OpenAI-compatible endpoint with retry logic.

    Args:
        prompt (str): The text prompt for the model.
        model_name (str): The name of the model to use.
        max_retries (int): Maximum number of retry attempts.
        temperature (float): Sampling temperature.

    Returns:
        str or None: The generated text, or None on failure.
    """
    client = OpenAI(
        api_key=DASHSCOPE_API_KEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    retries = 0
    sleep_time = 1

    while retries < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model_name if model_name else DEFAULT_DASHSCOPE_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                extra_body={"enable_thinking": False},
            )

            if completion and completion.choices:
                logger.debug(
                    f"Successfully called Dashscope OpenAI-compatible model '{model_name}' with prompt."
                )
                return completion.choices[0].message.content
            else:
                logger.warning(
                    f"Dashscope OpenAI-compatible API returned empty response: {completion}"
                )
                time.sleep(sleep_time)
                retries += 1
                logger.info(
                    f"Retrying in {sleep_time} seconds... (Attempt {retries} of {max_retries})"
                )

        except Exception as e:
            logger.error(
                f"An error occurred calling Dashscope OpenAI-compatible model '{model_name}' with prompt: {e}"
            )
            retries += 1
            if retries < max_retries:
                time.sleep(sleep_time)
            else:
                logger.error(
                    "Max retries reached for OpenAI-compatible call. Returning None."
                )
                return None

    return None


if __name__ == "__main__":
    # Example usage for Dashscope
    prompt = "Briefly introduce Dashscope."
    answer = dashscope_openai_api(
        prompt=prompt,
        model_name = "qwen3-235b-a22b"
    )
    if answer:
        print("Dashscope API Response:")
        print(answer)
    else:
        print("Failed to get a response from Dashscope API.")
