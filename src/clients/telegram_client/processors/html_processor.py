from jinja2 import Environment, FileSystemLoader

from src.clients.telegram_client.config import settings
from src.core.models import SearchResult
from datetime import datetime


class HTMLProcessor:
    def __init__(self):
        env = Environment(loader=FileSystemLoader(str(settings.templates_folder.resolve())))
        env.filters["date_format"] = HTMLProcessor.date_format
        self.template = env.get_template("search_response.html")

    async def process(self, search_results: list[SearchResult]) -> str:
        """Process text and return vector representation"""

        return self.template.render(search_results=search_results)

    @classmethod
    def date_format(cls, date_string: str, format: str = "%b %e") -> str:
        return datetime.fromisoformat(date_string).strftime(format)
