from mirascope.core import BaseTool, Messages, anthropic


class GetBookAuthor(BaseTool):
    title: str

    def call(self) -> str:
        if self.title == "The Name of the Wind":
            return "Patrick Rothfuss"
        elif self.title == "Mistborn: The Final Empire":
            return "Brandon Sanderson"
        else:
            return "Unknown"


@anthropic.call("claude-3-5-sonnet-20240620", tools=[GetBookAuthor])
def identify_author(
    book: str, history: list[anthropic.AnthropicMessageParam]
) -> Messages.Type:
    messages = [*history]
    if book:
        messages.append(Messages.User(f"Who wrote {book}?"))
    return messages


history = []
response = identify_author("The Name of the Wind", history)
history += [response.user_message_param, response.message_param]
while tool := response.tool:
    tools_and_outputs = [(tool, tool.call())]
    history += response.tool_message_params(tools_and_outputs)
    response = identify_author("", history)
    history.append(response.message_param)
print(response.content)
# Output: The Name of the Wind was written by Patrick Rothfuss.
