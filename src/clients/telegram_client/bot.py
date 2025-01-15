from dataclasses import dataclass
from typing import Optional
import io

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from clients.telegram_client.client import MemoAPIClient
from clients.telegram_client.config import settings
from clients.telegram_client.processors.html_processor import HTMLProcessor
from core.models import AudioData


@dataclass
class AudioMessage:
    file: io.BytesIO
    format: str
    duration: int
    user_id: str
    username: str


class TelegramBot:
    def __init__(self):
        self.memo_client = MemoAPIClient(settings.api_base_url)
        self.html_processor = HTMLProcessor()

    async def _extract_audio_message(self, update: Update) -> Optional[AudioMessage]:
        """Extract audio data from different types of messages."""
        if update.message.voice:
            audio_file = await update.message.voice.get_file()
            duration = update.message.voice.duration
            audio_format = "ogg"
        elif update.message.audio:
            audio_file = await update.message.audio.get_file()
            duration = update.message.audio.duration
            audio_format = update.message.audio.mime_type.split("/")[-1]
        else:
            return None

        buffer = io.BytesIO()
        await audio_file.download_to_memory(out=buffer)
        buffer.seek(0)

        return AudioMessage(
            file=buffer,
            format=audio_format,
            duration=duration,
            user_id=str(update.effective_chat.id),
            username=update.effective_user.first_name,
        )

    async def handle_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming audio messages."""
        audio_message = await self._extract_audio_message(update)
        if not audio_message:
            raise NotImplementedError("Unsupported message type")

        print(f"Received a voice message from {audio_message.username}")

        audio = AudioData(
            file=audio_message.file,
            format=audio_message.format,
            duration=audio_message.duration,
        )

        stored_memo = await self.memo_client.store_memo(audio, audio_message.user_id)
        html = await self.html_processor.process([stored_memo])
        await update.message.reply_html(html)

    async def handle_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text search queries."""
        print(f"Received a text message from {update.effective_user.first_name}")

        query = update.message.text
        user_id = str(update.effective_chat.id)

        response = await self.memo_client.search_memos(query, user_id)
        html = await self.html_processor.process(response["results"])
        await update.message.reply_html(html)

    def setup_handlers(self, application: Application) -> None:
        """Set up message handlers for the application."""
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_search))
        application.add_handler(MessageHandler((filters.VOICE | filters.AUDIO) & ~filters.COMMAND, self.handle_audio))

    def run(self) -> None:
        """Start the bot and run it indefinitely."""
        application = Application.builder().token(settings.telegram_api_token).build()
        self.setup_handlers(application)
        application.run_polling(allowed_updates=Update.ALL_TYPES, poll_interval=5)


def main() -> None:
    bot = TelegramBot()
    bot.run()


if __name__ == "__main__":
    main()
