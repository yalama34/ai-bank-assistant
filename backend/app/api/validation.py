from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.models.draft import Draft
from app.models.letter import Letter
from app.schemas.validation import ValidationResult
from app.services.validation import ValidationService

router = APIRouter(
    prefix="/validation",
    tags=["validation"],
    dependencies=[Depends(verify_api_key)],
)


@router.post(
    "/validate/{draft_id}",
    response_model=ValidationResult,
)
async def validate_draft(
    draft_id: int,
    db: AsyncSession = Depends(get_db),
) -> Any:
    draft = await db.get(Draft, draft_id)
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )

    letter = await db.get(Letter, draft.letter_id)
    if not letter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Letter not found",
        )

    validation_service = ValidationService(db=db)
    validation_result = await validation_service.validate_response(
        response=draft.content,
        original_letter=letter.content,
        style=draft.style,
    )

    draft.validation_score = validation_result.score
    draft.validation_result = validation_result.model_dump()
    
    if validation_result.auto_send_eligible:
        draft.status = "validated"
    else:
        draft.status = "draft"

    db.add(draft)
    await db.commit()
    await db.refresh(draft)

    return validation_result

