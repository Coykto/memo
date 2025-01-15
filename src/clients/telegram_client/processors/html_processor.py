from jinja2 import Environment, FileSystemLoader

from clients.telegram_client.config import settings
from core.models import SearchResult


class HTMLProcessor:
    def __init__(self):
        env = Environment(loader=FileSystemLoader(str(settings.templates_folder.resolve())))
        self.template = env.get_template("search_response.html")

    async def process(self, search_results: list[SearchResult]) -> str:
        """Process text and return vector representation"""

        return self.template.render(search_results=search_results)
