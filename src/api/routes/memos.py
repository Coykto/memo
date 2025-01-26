import logging

from fastapi import APIRouter, Depends, File, UploadFile

from src.api.dependencies import get_memo_service
from src.api.schemas import MemoResponse
from src.core.models import AudioData
from src.core.services.memo import MemoService

router = APIRouter(prefix="/memos")


@router.post("/", response_model=MemoResponse)
async def create_memo(
        user_id: str,
        audio: UploadFile = File(...),
        memo_service: MemoService = Depends(get_memo_service),
):
    audio_data = AudioData(
        file=audio.file,
        format=audio.filename.split(".")[-1],
    )

    memo = await memo_service.create_memo_from_audio(audio_data, user_id)
    return MemoResponse.from_memo(memo)


@router.get("/")
async def check():
    logging.info("Check request")
    return {"message": "ok"}
