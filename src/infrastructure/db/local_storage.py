import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from src.core.models import Memo
from src.config.settings import Settings
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

    async def store_memo(self, text: str, title: str, user_id: str) -> str:
        """Store memo text and return memo ID"""
        db = json.load(open(self.db_file))
        memo_id = str(uuid4())
        if user_id in db:
            db[user_id][memo_id] = {
                "text": text,
                "title": title,
                "date": datetime.now().isoformat(),
            }
        else:
            db[user_id] = {
                memo_id: {
                    "text": text,
                    "title": title,
                    "date": datetime.now().isoformat(),
                }
            }
        json.dump(db, open(self.db_file, "w"), indent=4, ensure_ascii=False)
        return memo_id

    async def get_memo(self, memo_id: str) -> Optional[Memo]:
        """Retrieve memo text by ID"""
        db = json.load(open(self.db_file))
        for user_id in db:
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
