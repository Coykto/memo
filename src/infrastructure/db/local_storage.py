import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from zlib import crc32

from src.config.settings import Settings
from src.core.models import Memo
from src.infrastructure.db.base import Storage


class LocalStorage(Storage):

    def __init__(self, settings: Settings):
        super().__init__()
        self.db_file = Path(settings.data_folder / "db.json")
        self._ensure_file_exists()
        logging.info("initialized local db")

    def _ensure_file_exists(self):
        if not os.path.exists(self.db_file):
            json.dump({}, open(self.db_file, "w"), indent=4, ensure_ascii=False)

    def _generate_id(self, text: str, title: str, user_id: str, date: datetime):
        message_data = f"{user_id}:{date.isoformat()}:{title}:{text}"
        crc = crc32(message_data.encode()) & 0xFFFFF
        return str(abs(crc))

    async def store_memo(self, text: str, title: str, user_id: str) -> str:
        """Store memo text and return memo ID"""
        db = json.load(open(self.db_file))
        message_date = datetime.now()
        memo_id = self._generate_id(text, title, user_id, message_date)
        if user_id in db:
            db[user_id][memo_id] = {
                "text": text,
                "title": title,
                "date": message_date.isoformat(),
            }
        else:
            db[user_id] = {
                memo_id: {
                    "text": text,
                    "title": title,
                    "date": message_date.isoformat(),
                }
            }
        json.dump(db, open(self.db_file, "w"), indent=4, ensure_ascii=False)
        return memo_id

    async def get_memo(self, user_id: str, memo_id: str) -> Optional[Memo]:
        """Retrieve memo text by ID"""
        db = json.load(open(self.db_file))
        if memo_id in db[user_id]:
            logging.info(f"Retrieved memo from local db {db[user_id][memo_id]}")
            return Memo(
                id=memo_id,
                text=db[user_id][memo_id]["text"],
                title=db[user_id][memo_id]["title"],
                date=db[user_id][memo_id]["date"],
                user_id=user_id,
            )
        return None

    async def delete_memo(self, user_id: str, memo_id: str) -> Optional[Memo]:
        """Delete memo by ID"""
        db = json.load(open(self.db_file))
        if memo_id in db[user_id]:
            memo = Memo(
                id=memo_id,
                text=db[user_id][memo_id]["text"],
                title=db[user_id][memo_id]["title"],
                date=db[user_id][memo_id]["date"],
                user_id=user_id,
            )
            del db[user_id][memo_id]
            json.dump(db, open(self.db_file, "w"), indent=4, ensure_ascii=False)
            return memo
        return None
