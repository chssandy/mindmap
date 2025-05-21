from collections.abc import Generator
import tempfile
from typing import Any
import subprocess
import os
import uuid

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.enum import filetype
from tools.utils.param_util import get_input_text

def convert_markdown_to_markmap(markdown_text):
    """
    将Markdown文本转换为Markmap JSON格式。
    
    :param markdown_text: 输入的Markdown文本
    :return: 提取出来的JSON字符串
    """
    # 创建临时文件保存Markdown内容
    with tempfile.NamedTemporaryFile(mode='w+', suffix=".md", delete=False) as md_file:
        md_file.write(markdown_text)
        md_path = md_file.name
    
    try:
        # 创建临时HTML文件用于存储输出
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as html_file:
            html_path = html_file.name
        
        # 使用 markmap 生成 HTML 文件
        subprocess.run(
            ['markmap', '--no-open', f'--output={html_path}', md_path],
            check=True
        )

        # 读取 HTML 文件
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    
    finally:
        import os
        os.remove(md_path)  # 清理临时Markdown文件
        os.remove(html_path)  # 清理临时HTML文件

class MindmapTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        invoke tools
        """
        # get parameters
        md_text = get_input_text(tool_parameters)
        output_filename = f"{str(uuid.uuid4()).upper()}{filetype.FileType.HTML}"

        try:
            json_output = convert_markdown_to_markmap(md_text)
            result_file_bytes = json_output.encode("utf-8")
        except Exception as e:
            yield self.create_text_message(f"Failed to convert markdown text to HTML file, error: {str(e)}")
            return

        yield self.create_blob_message(
            blob=result_file_bytes,
            meta = {
                "mime_type": filetype.FileType.get_mime(filetype.FileType.HTML),
                "filename": output_filename,
            },
        )
        return
        
        
    

