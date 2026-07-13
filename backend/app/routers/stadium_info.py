"""Stadium information read endpoints.

Provides the data layer that both personas consume:
    - Fan Assistant uses these via Gemini function calling to ground
      responses in real stadium data (zones, facilities, transport, FAQs).
    - Ops Dashboard reads zone/gate data for the live status display.

All endpoints are GET-only, read-only, and return Pydantic-validated JSON.
Query parameters provide optional filtering (by type, zone, category)
without requiring separate endpoint variants.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.facility import Facility
from app.models.faq import FAQEntry
from app.models.gate import Gate
from app.models.transport import TransportOption
from app.models.zone import Zone
from app.schemas.facility import FacilityResponse
from app.schemas.faq import FAQResponse
from app.schemas.gate import GateResponse
from app.schemas.transport import TransportResponse
from app.schemas.zone import ZoneDetail, ZoneSummary

router = APIRouter(prefix="/api/v1/stadium", tags=["stadium"])


# ── Zones ────────────────────────────────────────────────────


@router.get("/zones", response_model=list[ZoneSummary])
async def list_zones(
    session: AsyncSession = Depends(get_session),
    zone_type: str | None = Query(
        None, description="Filter by zone type: seating, concourse, vip"
    ),
) -> list[Zone]:
    """List all stadium zones with current occupancy.

    Returns lightweight zone summaries with computed density percentage.
    Optionally filter by zone_type (seating, concourse, vip).
    """
    stmt = select(Zone)
    if zone_type:
        stmt = stmt.where(Zone.zone_type == zone_type)
    stmt = stmt.order_by(Zone.id)

    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.get("/zones/{zone_id}", response_model=ZoneDetail)
async def get_zone(
    zone_id: str,
    session: AsyncSession = Depends(get_session),
) -> Zone:
    """Get detailed zone information including gates and facilities.

    Returns the full zone data with nested relationships.
    Gates and facilities are eagerly loaded (selectin strategy
    defined in the ORM model).
    """
    result = await session.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()
    if zone is None:
        raise HTTPException(status_code=404, detail=f"Zone '{zone_id}' not found")
    return zone


# ── Gates ────────────────────────────────────────────────────


@router.get("/gates", response_model=list[GateResponse])
async def list_gates(
    session: AsyncSession = Depends(get_session),
    zone_id: str | None = Query(None, description="Filter gates by zone"),
    accessible_only: bool = Query(False, description="Only show accessible gates"),
) -> list[Gate]:
    """List all gates with current queue status and estimated wait times.

    Filterable by zone and accessibility. The estimated_wait_minutes
    in the response is computed from queue_length / throughput_rate.
    """
    stmt = select(Gate)
    if zone_id:
        stmt = stmt.where(Gate.zone_id == zone_id)
    if accessible_only:
        stmt = stmt.where(Gate.is_accessible.is_(True))
    stmt = stmt.order_by(Gate.id)

    result = await session.execute(stmt)
    return list(result.scalars().all())


# ── Facilities ───────────────────────────────────────────────


@router.get("/facilities", response_model=list[FacilityResponse])
async def list_facilities(
    session: AsyncSession = Depends(get_session),
    facility_type: str | None = Query(
        None,
        description="Filter by type: restroom, first_aid, food_beverage, prayer_room, baby_care, lost_found",
    ),
    zone_id: str | None = Query(None, description="Filter by zone"),
    accessible_only: bool = Query(False, description="Only show accessible facilities"),
) -> list[Facility]:
    """List stadium facilities with optional filtering.

    Supports filtering by facility_type, zone, and accessibility.
    This endpoint powers the fan assistant's "find nearest restroom"
    type queries via Gemini function calling.
    """
    stmt = select(Facility)
    if facility_type:
        stmt = stmt.where(Facility.facility_type == facility_type)
    if zone_id:
        stmt = stmt.where(Facility.zone_id == zone_id)
    if accessible_only:
        stmt = stmt.where(Facility.is_accessible.is_(True))
    stmt = stmt.order_by(Facility.zone_id, Facility.facility_type)

    result = await session.execute(stmt)
    return list(result.scalars().all())


# ── Transport ────────────────────────────────────────────────


@router.get("/transport", response_model=list[TransportResponse])
async def list_transport(
    session: AsyncSession = Depends(get_session),
    transport_type: str | None = Query(
        None,
        description="Filter by type: metro, bus, taxi, rideshare, parking",
    ),
) -> list[TransportOption]:
    """List transport options to/from the stadium.

    Optionally filter by transport_type. Each option includes
    the nearest gate, walk time, and accessibility details.
    """
    stmt = select(TransportOption)
    if transport_type:
        stmt = stmt.where(TransportOption.transport_type == transport_type)
    stmt = stmt.order_by(TransportOption.transport_type, TransportOption.name)

    result = await session.execute(stmt)
    return list(result.scalars().all())


# ── FAQs ─────────────────────────────────────────────────────


@router.get("/faqs", response_model=list[FAQResponse])
async def list_faqs(
    session: AsyncSession = Depends(get_session),
    category: str | None = Query(
        None,
        description="Filter by category: general, accessibility, safety, food, transport, rules",
    ),
    search: str | None = Query(
        None,
        description="Search FAQ questions and tags (case-insensitive substring match)",
        max_length=100,
    ),
) -> list[FAQEntry]:
    """List FAQ entries with optional category and search filtering.

    The search parameter does a case-insensitive substring match
    against question text and tags. This is the retrieval mechanism
    the Gemini function calling uses when fans ask questions.
    """
    stmt = select(FAQEntry)
    if category:
        stmt = stmt.where(FAQEntry.category == category)
    if search:
        search_pattern = f"%{search}%"
        stmt = stmt.where(
            FAQEntry.question.ilike(search_pattern)
            | FAQEntry.tags.ilike(search_pattern)
        )
    stmt = stmt.order_by(FAQEntry.category, FAQEntry.id)

    result = await session.execute(stmt)
    return list(result.scalars().all())
