from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import verify_api_key
from ..models.correspondence_history import CorrespondenceHistory
from ..models.draft import Draft
from ..models.letter import Letter
from ..schemas.processing_params import ProcessingParams
from ..services.generation import GenerationService

router = APIRouter(
    prefix="/generation",
    tags=["generation"],
    dependencies=[Depends(verify_api_key)],
)


@router.post(
    "/generate/{letter_id}",
    response_model=Any,
)
async def generate_response(
    letter_id: int,
    db: AsyncSession = Depends(get_db),
) -> Any:
    letter = await db.get(Letter, letter_id)
    if not letter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Letter not found",
        )

    result = await db.execute(
        select(CorrespondenceHistory).where(
            CorrespondenceHistory.correspondence_thread_id == letter.correspondence_thread_id
        )
    )
    correspondence_history = result.scalars().all()

    if letter.processing_params:
        if isinstance(letter.processing_params, dict):
            processing_params = ProcessingParams.model_validate(letter.processing_params)
        else:
            processing_params = letter.processing_params
    else:
        processing_params = ProcessingParams()

    generation_service = GenerationService(db=db)
    generated_content = await generation_service.generate_response(
        letter_content=letter.content,
        processing_params=processing_params,
        correspondence_history=correspondence_history,
    )

    draft = Draft(
        letter_id=letter.id,
        content=generated_content,
        style=processing_params.response_style or processing_params.formality_level,
        status="draft",
    )
    db.add(draft)
    await db.commit()
    await db.refresh(draft)

    return draft
