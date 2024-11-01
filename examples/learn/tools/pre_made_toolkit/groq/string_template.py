from mirascope.core import groq, BaseDynamicConfig, prompt_template
from mirascope.tools import FileSystemToolkit
from pathlib import Path


@groq.call("llama-3.1-70b-versatile")
@prompt_template("Write a blog post about '{topic}' as a '{output_file.name}'.")
def write_blog_post(topic: str, output_file: Path) -> BaseDynamicConfig:
    toolkit = FileSystemToolkit(base_directory=output_file.parent)
    return {
        "tools": toolkit.create_tools(),
    }


response = write_blog_post("machine learning", Path("introduction.html"))
if tool := response.tool:
    result = tool.call()
    print(result)
