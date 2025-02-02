from unittest.mock import AsyncMock

import pytest
from telegram import Chat, Message, Update, User

from src.clients.telegram_client.bot import TelegramBot


async def test_handle_message_deletion_success():
    # Setup test data
    test_user_id = "123456"
    test_memo_id = "test-memo-123"
    test_command = f"/del_{test_memo_id}"

    # Create mock update
    mock_message = AsyncMock(spec=Message)
    mock_message.text = test_command
    mock_message.reply_html = AsyncMock()

    mock_chat = AsyncMock(spec=Chat)
    mock_chat.id = test_user_id

    mock_user = AsyncMock(spec=User)
    mock_user.first_name = "Test User"

    mock_update = AsyncMock(spec=Update)
    mock_update.message = mock_message
    mock_update.effective_chat = mock_chat
    mock_update.effective_user = mock_user

    # Create mock API client
    mock_api_client = AsyncMock()
    mock_api_client.delete_memo.return_value = {
        "results": [
            {
                "id": test_memo_id,
                "text": "Test memo content",
                "title": "Test memo title",
                "date": "2025-02-01T15:18:15.024307",
            }
        ]
    }

    # Create bot instance with mock client
    bot = TelegramBot()
    bot.memo_client = mock_api_client

    # Execute handler
    await bot.handle_message_deletion(mock_update, None)

    # Verify API client was called correctly
    mock_api_client.delete_memo.assert_called_once_with(test_user_id, test_memo_id)

    # Verify response was sent
    mock_message.reply_html.assert_called_once()
    args = mock_message.reply_html.call_args[0]
    assert "Deleted Memo" in args[0]


async def test_handle_message_deletion_api_error():
    # Setup test data
    test_user_id = "123456"
    test_memo_id = "test-memo-123"
    test_command = f"/del_{test_memo_id}"

    # Create mock update
    mock_message = AsyncMock(spec=Message)
    mock_message.text = test_command
    mock_message.reply_html = AsyncMock()

    mock_chat = AsyncMock(spec=Chat)
    mock_chat.id = test_user_id

    mock_update = AsyncMock(spec=Update)
    mock_update.message = mock_message
    mock_update.effective_chat = mock_chat

    # Create mock API client that raises an error
    mock_api_client = AsyncMock()
    mock_api_client.delete_memo.side_effect = Exception("API Error")

    # Create bot instance with mock client
    bot = TelegramBot()
    bot.memo_client = mock_api_client

    # Execute handler and verify error handling
    with pytest.raises(Exception) as exc_info:
        await bot.handle_message_deletion(mock_update, None)

    assert "API Error" in str(exc_info.value)
    mock_api_client.delete_memo.assert_called_once_with(test_user_id, test_memo_id)
