from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import verify_api_key
from ..models.letter import Letter
from ..schemas.letter import LetterCreate, LetterResponse
from ..schemas.processing_params import ProcessingParams
from ..services.analysis import AnalysisService

router = APIRouter(
    prefix="/letters",
    tags=["letters"],
    dependencies=[Depends(verify_api_key)],
)


@router.post(
    "/",
    response_model=LetterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_letter(
    payload: LetterCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Создание письма:
    1. Валидация LetterCreate (автоматически через Pydantic)
    2. Создание Letter в БД
    3. Вызов AnalysisService.analyze_letter()
    4. Обновление Letter с processing_params и request_category
    5. Возврат LetterResponse
    """
    letter = Letter(
        subject=payload.subject,
        content=payload.content,
        sender=payload.sender,
        sender_email=payload.sender_email,
        client_id=payload.client_id,
        correspondence_thread_id=payload.correspondence_thread_id,
    )
    db.add(letter)
    await db.commit()
    await db.refresh(letter)

    analysis_service = AnalysisService(db=db)
    analysis_result = await analysis_service.analyze_letter(letter_content=letter.content)

    
    
    if hasattr(analysis_result, "processing_params"):
        processing_params_data = analysis_result.processing_params
    elif isinstance(analysis_result, dict):
        processing_params_data = analysis_result.get("processing_params")
    else:
        processing_params_data = None

    if hasattr(analysis_result, "request_category"):
        request_category = analysis_result.request_category
    elif isinstance(analysis_result, dict):
        request_category = analysis_result.get("request_category")
    else:
        request_category = None

    
    if processing_params_data:
        if isinstance(processing_params_data, dict):
            letter.processing_params = processing_params_data
        else:
            # Если это Pydantic модель, преобразуем в dict
            letter.processing_params = ProcessingParams.model_validate(
                processing_params_data
            ).model_dump()

    if request_category:
        letter.request_category = request_category

    db.add(letter)
    await db.commit()
    await db.refresh(letter)

    return LetterResponse.model_validate(letter)


@router.get(
    "/",
    response_model=List[LetterResponse],
)
async def get_letters(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Получение всех писем.
    """
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(Letter)
        .options(selectinload(Letter.drafts), selectinload(Letter.approvals))
        .order_by(Letter.received_at.desc())
    )
    letters = result.scalars().all()
    return [LetterResponse.model_validate(letter) for letter in letters]


@router.get(
    "/{letter_id}",
    response_model=LetterResponse,
)
async def get_letter(
    letter_id: int,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Получение письма по ID.
    """
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(Letter)
        .options(selectinload(Letter.drafts), selectinload(Letter.approvals))
        .where(Letter.id == letter_id)
    )
    letter = result.scalar_one_or_none()
    if not letter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Letter not found",
        )

    return LetterResponse.model_validate(letter)