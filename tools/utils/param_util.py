import re
from typing import Any

THINK_TAG_REGEX = re.compile(r'<think>.*?</think>', flags=re.DOTALL)

def get_input_text(tool_parameters: dict[str, Any]) -> str:
    input_text = tool_parameters.get("query", "")
    if not input_text:
        raise ValueError(f"Empty input text")
    input_text = THINK_TAG_REGEX.sub('', input_text)

    input_text = strip_wrapper(input_text, 'markdown')
    input_text = input_text.replace("\\\\", "\\")
    input_text = input_text.replace("\\n", "\n")
    
    if not input_text:
        raise ValueError(f"Empty input text")
    return input_text

def strip_wrapper(text: str, input_type: str) -> str:
    """
    移除文本两端的空白字符以及可能存在的代码块包裹符号（如 ```markdown ... ```）。

    参数:
    - text: 输入的文本字符串。
    - mime_type: 动态传入的 MIME 类型，用于识别代码块类型（如 markdown）。

    返回:
    - 去除包裹符号和空格后的文本。
    """
    # 去除首尾空白字符
    text = text.strip()
    wrapper = "```"
    # 如果文本以代码块结束符结尾，则尝试去除包裹符号
    if text.endswith(wrapper):
        if text.startswith(f"{wrapper}{input_type}"):
            # 带 MIME 类型的包裹符，去除前缀和后缀
            text = text[(len(f"{wrapper}{input_type}")): -len(wrapper)]
        elif text.startswith(wrapper):
            # 完全匹配包裹符，直接去除前后包裹符
            text = text[len(wrapper): -len(wrapper)]
    return text

