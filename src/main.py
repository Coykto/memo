import io

from adapters.db.local import LocalDB
from adapters.summary.claude_summary import ClaudeSummaryAdapter
from adapters.transcription.open_ai_transcription import OpenAITranscriptionAdapter
from adapters.vector_db.pinecone_db import PineconeAdapter
from adapters.vectorization.open_ai_vectorization import OpenAIVectorizationAdapter
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from clients.telegram_client.processors.html_processor import HTMLProcessor
from config.settings import settings
from core.models import AudioData
from core.services.audio import AudioService
from core.services.search import SearchEngine
from core.services.text import TextProcessor

search_engine = SearchEngine(
    audio_processor=AudioService(transcription_service=OpenAITranscriptionAdapter()),
    text_processor=TextProcessor(vectorization_adapter=OpenAIVectorizationAdapter()),
    vector_db_adapter=PineconeAdapter(),
    database_adapter=LocalDB(),
    summary_adapter=ClaudeSummaryAdapter(),
)


async def store_memo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_chat.id)
    if update.message.voice:
        print(f"Received a voice message from {update.effective_user.first_name}")
        audio_file = await update.message.voice.get_file()
        duration = update.message.voice.duration
        audio_format = "ogg"
    elif update.message.audio:
        print(f"Received an audio message from {update.effective_user.first_name}")
        audio_file = await update.message.audio.get_file()
        duration = update.message.audio.duration
        audio_format = update.message.audio.mime_type.split("/")[-1]
    else:
        raise NotImplementedError

    buffer = io.BytesIO()
    await audio_file.download_to_memory(out=buffer)
    buffer.seek(0)

    audio = AudioData(
        file=buffer,
        format=audio_format,
        duration=duration,
    )

    stored_memo = await search_engine.store_memo(audio, user_id)
    html = await HTMLProcessor().process([stored_memo])
    await update.message.reply_html(html)


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Received a text message from {update.effective_user.first_name}")
    query = update.message.text
    user_id = str(update.effective_chat.id)
    results = await search_engine.search(query, user_id)

    html = await HTMLProcessor().process(results)
    await update.message.reply_html(html)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(settings.telegram_api_token).build()

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
    application.add_handler(MessageHandler(filters.VOICE & ~filters.COMMAND, store_memo))
    application.add_handler(MessageHandler(filters.AUDIO & ~filters.COMMAND, store_memo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES, poll_interval=5)


if __name__ == "__main__":
    main()
