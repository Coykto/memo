import logging

import anthropic
from anthropic._exceptions import RateLimitError
from tenacity import (before_sleep_log, retry, retry_if_exception_type,
                      stop_after_attempt, wait_exponential)

from src.core.models import Summary
from src.infrastructure.summarization.base import Summarizer


class ClaudeSummarizer(Summarizer):

    def __init__(self, api_key: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = anthropic.Anthropic(api_key=api_key)

    @retry(
        wait=wait_exponential(min=3, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(RateLimitError),
        before_sleep=before_sleep_log(logging.getLogger(), logging.WARNING),
    )
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
