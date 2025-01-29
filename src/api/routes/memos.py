from fastapi import APIRouter, Depends, File, UploadFile

from src.api.dependencies import get_memo_service
from src.api.schemas import MemoResponse
from src.core.models import AudioData
from src.core.services.memo import MemoService

router = APIRouter(prefix="/v1/memos")


@router.post(
    "/",
    response_model=MemoResponse,
    summary="Create Voice Memo",
    description="""
    Create a new voice memo from an audio file.
    
    Supported audio formats: flac, m4a, mp3, mp4, mpeg, mpga, oga, ogg, wav, webm
    Maximum file size: 25MB
    Maximum audio duration: 10 minutes""",
)
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
