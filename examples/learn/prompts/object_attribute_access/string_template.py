from mirascope.core import prompt_template
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str


@prompt_template("I read {book.title} by {book.author}. What should I read next?")
def recommend_book_prompt(book: Book): ...


book = Book(title="The Name of the Wind", author="Patrick Rothfuss")
print(recommend_book_prompt(book))
# Output: [BaseMessageParam(role='user', content='I read The Name of the Wind by Patrick Rothfuss. What should I read next?')]