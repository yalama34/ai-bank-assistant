from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.models.approval import Approval
from app.models.draft import Draft
from app.models.letter import Letter
from app.schemas.processing_params import ProcessingParams
from app.services.routing import RoutingService

router = APIRouter(
    prefix="/approval",
    tags=["approval"],
    dependencies=[Depends(verify_api_key)],
)


@router.post(
    "/route/{letter_id}",
    response_model=Any,
)
async def route_letter(
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
        select(Draft)
        .where(Draft.letter_id == letter_id)
        .order_by(Draft.created_at.desc())
    )
    draft = result.scalar_one_or_none()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found for this letter",
        )

    if draft.validation_score and draft.validation_score >= 80:
        draft.status = "sent"
        db.add(draft)
        await db.commit()
        await db.refresh(draft)

        approval = Approval(
            letter_id=letter.id,
            draft_id=draft.id,
            approval_status="auto_sent",
            route=[],
        )
        db.add(approval)
        await db.commit()
        await db.refresh(approval)
        
        return approval

    if letter.processing_params:
        if isinstance(letter.processing_params, dict):
            processing_params = ProcessingParams.model_validate(letter.processing_params)
        else:
            processing_params = letter.processing_params
    else:
        processing_params = ProcessingParams()

    routing_service = RoutingService(db=db)
    route_data = await routing_service.determine_route(processing_params=processing_params)

    approval = Approval(
        letter_id=letter.id,
        draft_id=draft.id,
        route=route_data.get("route", []),
        current_approver=route_data.get("current_approver"),
        approval_status="pending",
        operation_amount=route_data.get("operation_amount"),
        request_category=route_data.get("request_category"),
        department=route_data.get("department"),
        risk_level=route_data.get("risk_level"),
        geography=route_data.get("geography"),
        client_type=route_data.get("client_type"),
        document_type=route_data.get("document_type"),
        change_type=route_data.get("change_type"),
    )
    db.add(approval)
    await db.commit()
    await db.refresh(approval)

    return approval


@router.get(
    "/status/{approval_id}",
    response_model=Any,
)
async def get_approval_status(
    approval_id: int,
    db: AsyncSession = Depends(get_db),
) -> Any:
    approval = await db.get(Approval, approval_id)
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found",
        )

    return approval

