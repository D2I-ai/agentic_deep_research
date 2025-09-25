import re


def is_chinese(string):
    """
    Check if the input string contains any Chinese characters.

    Chinese character Unicode range: \u4e00 - \u9fff
    """
    try:
        # Use regular expression to search for any Chinese character in the string
        return bool(re.search(r"[\u4e00-\u9fff]", string))
    except Exception:
        # In case of unexpected error, default to True
        return True


def is_english(text):
    """
    Determine whether English characters make up more than half of the total characters in the text.

    Args:
        text (str): Input text.

    Returns:
        bool: True if English characters account for more than half; otherwise, False.
    """
    if not text:
        return False

    total_chars = len(text)
    english_chars = sum(1 for c in text if c.isalpha() and c.encode().isascii())

    return english_chars > total_chars / 2
