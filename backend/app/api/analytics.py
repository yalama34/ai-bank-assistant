from datetime import datetime, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.models.draft import Draft
from app.models.letter import Letter
from app.schemas.processing_params import ProcessingParams

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[Depends(verify_api_key)],
)


@router.get(
    "/metrics",
    response_model=Dict[str, Any],
)
async def get_metrics(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    letters_result = await db.execute(select(Letter))
    letters = letters_result.scalars().all()

    drafts_result = await db.execute(select(Draft))
    drafts = drafts_result.scalars().all()

    processing_times = []
    letter_types_count: Dict[str, int] = {}
    status_distribution: Dict[str, int] = {}

    for letter in letters:
        if letter.received_at:
            letter_drafts = [d for d in drafts if d.letter_id == letter.id]
            if letter_drafts:
                sent_draft = next(
                    (d for d in letter_drafts if d.status == "sent"),
                    None
                )
                if sent_draft and sent_draft.updated_at:
                    processing_time = (sent_draft.updated_at - letter.received_at).total_seconds() / 3600
                    processing_times.append(processing_time)

        if letter.processing_params:
            if isinstance(letter.processing_params, dict):
                params = letter.processing_params
            else:
                params = ProcessingParams.model_validate(letter.processing_params).model_dump()
            
            letter_type = params.get("letter_type") or letter.request_category or "unknown"
            letter_types_count[letter_type] = letter_types_count.get(letter_type, 0) + 1
        else:
            letter_type = letter.request_category or "unknown"
            letter_types_count[letter_type] = letter_types_count.get(letter_type, 0) + 1

    for draft in drafts:
        status = draft.status or "unknown"
        status_distribution[status] = status_distribution.get(status, 0) + 1

    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0

    return {
        "average_processing_time_hours": round(avg_processing_time, 2),
        "letter_types_statistics": letter_types_count,
        "status_distribution": status_distribution,
        "total_letters": len(letters),
        "total_drafts": len(drafts),
    }


@router.get(
    "/sla",
    response_model=Dict[str, Any],
)
async def get_sla_monitoring(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    letters_result = await db.execute(select(Letter))
    letters = letters_result.scalars().all()

    drafts_result = await db.execute(select(Draft))
    drafts = drafts_result.scalars().all()

    violated_letters = []
    sla_compliance_count = 0
    sla_violation_count = 0

    for letter in letters:
        if not letter.received_at:
            continue

        if letter.processing_params:
            if isinstance(letter.processing_params, dict):
                params = letter.processing_params
            else:
                params = ProcessingParams.model_validate(letter.processing_params).model_dump()
            
            sla_deadline_str = params.get("sla_deadline")
            if sla_deadline_str:
                if isinstance(sla_deadline_str, str):
                    sla_deadline = datetime.fromisoformat(sla_deadline_str.replace("Z", "+00:00"))
                elif isinstance(sla_deadline_str, datetime):
                    sla_deadline = sla_deadline_str
                else:
                    continue
            else:
                continue
        else:
            continue

        letter_drafts = [d for d in drafts if d.letter_id == letter.id]
        sent_draft = next(
            (d for d in letter_drafts if d.status == "sent"),
            None
        )

        now = datetime.utcnow()
        if sent_draft:
            if sent_draft.updated_at and sent_draft.updated_at > sla_deadline:
                sla_violation_count += 1
                violated_letters.append({
                    "letter_id": letter.id,
                    "subject": letter.subject,
                    "received_at": letter.received_at.isoformat() if letter.received_at else None,
                    "sla_deadline": sla_deadline.isoformat(),
                    "sent_at": sent_draft.updated_at.isoformat() if sent_draft.updated_at else None,
                    "violation_hours": round((sent_draft.updated_at - sla_deadline).total_seconds() / 3600, 2),
                })
            else:
                sla_compliance_count += 1
        else:
            if now > sla_deadline:
                sla_violation_count += 1
                violated_letters.append({
                    "letter_id": letter.id,
                    "subject": letter.subject,
                    "received_at": letter.received_at.isoformat() if letter.received_at else None,
                    "sla_deadline": sla_deadline.isoformat(),
                    "sent_at": None,
                    "violation_hours": round((now - sla_deadline).total_seconds() / 3600, 2),
                })
            else:
                sla_compliance_count += 1

    total_checked = sla_compliance_count + sla_violation_count
    compliance_rate = (sla_compliance_count / total_checked * 100) if total_checked > 0 else 0

    return {
        "sla_compliance_rate_percent": round(compliance_rate, 2),
        "sla_compliant_count": sla_compliance_count,
        "sla_violated_count": sla_violation_count,
        "violated_letters": violated_letters,
        "total_checked": total_checked,
    }

