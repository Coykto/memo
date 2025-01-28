import anthropic

from src.core.models import Summary
from src.infrastructure.summarization.base import Summarizer


class ClaudeSummarizer(Summarizer):

    def __init__(self, api_key: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = anthropic.Anthropic(api_key=api_key)

    async def summarize(self, text: str, length: int = 50) -> Summary:
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=(
                "Generate only a single line containing a clear, "
                "specific title (max 50 characters) that captures "
                "the core topic or action of this voice memo. "
                "Return nothing else but the title itself."
            ),
            messages=[{"role": "user", "content": text}],
        )
        return Summary(
            text=text,
            summary=message.content[0].text,
        )
