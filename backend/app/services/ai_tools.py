"""AI Tools for Gemini Function Calling.

These functions are passed directly to the google-genai SDK.
Gemini reads their docstrings and type hints to understand when and how
to call them. When the AI decides it needs stadium data, it calls these
functions, we execute them against the DB, and the SDK feeds the result
back to the model.
"""

import structlog
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core import database
from app.models.facility import Facility
from app.models.faq import FAQEntry
from app.models.gate import Gate
from app.models.transport import TransportOption
from app.models.zone import Zone

logger = structlog.get_logger(__name__)


async def get_zone_status(zone_id: str) -> dict:
    """Get real-time occupancy and gate queue status for a specific stadium zone.

    Use this when the fan asks about crowds, how busy a section is, or wait
    times for gates at a specific stand.

    Args:
        zone_id: The ID of the zone (e.g., 'north_stand', 'fan_zone').
    """
    logger.info("tool_called", tool="get_zone_status", zone_id=zone_id)
    try:
        async with database._async_session_factory() as session:
            stmt = select(Zone).options(selectinload(Zone.gates)).where(Zone.id == zone_id)
            result = await session.execute(stmt)
            zone = result.scalar_one_or_none()
            
            if not zone:
                return {"error": f"Zone '{zone_id}' not found. Valid zones include north_stand, south_stand, fan_zone, etc."}
            
        density = (zone.current_occupancy / max(zone.capacity, 1)) * 100
        
        gate_info = []
        for gate in zone.gates:
            wait_time = round(gate.current_queue_length / max(gate.capacity_per_minute, 1), 1)
            gate_info.append({
                "gate_name": gate.name,
                "type": gate.gate_type,
                "queue_length": gate.current_queue_length,
                "estimated_wait_minutes": wait_time
            })
            
            return {
                "zone_name": zone.name,
                "current_occupancy": zone.current_occupancy,
                "capacity": zone.capacity,
                "density_percent": round(density, 1),
                "gates": gate_info
            }
    except Exception as e:
        logger.error("tool_error", tool="get_zone_status", error=str(e))
        import traceback
        with open("tool_error.txt", "w") as f:
            f.write(traceback.format_exc())
        return {"error": f"Internal database error: {str(e)}"}


async def find_facilities(facility_type: str, accessible_only: bool = False) -> list:
    """Find facilities in the stadium like restrooms, food, or first aid.

    Use this when a fan asks where to eat, where the bathroom is, or needs medical help.

    Args:
        facility_type: Must be one of: 'restroom', 'first_aid', 'food_beverage', 'prayer_room', 'baby_care', 'lost_found'.
        accessible_only: Set to true if the fan explicitly asks for wheelchair accessible facilities.
    """
    logger.info("tool_called", tool="find_facilities", type=facility_type)
    
    # Handle common pluralization mistakes from the model
    if facility_type.endswith("s") and facility_type != "first_aid":
        facility_type = facility_type[:-1]
        
    try:
        async with database._async_session_factory() as session:
            stmt = select(Facility).where(Facility.facility_type == facility_type)
            if accessible_only:
                stmt = stmt.where(Facility.is_accessible.is_(True))
                
            result = await session.execute(stmt)
            facilities = list(result.scalars().all())
            
            if not facilities:
                return {"note": f"No facilities of type '{facility_type}' found."}
                
            return [
                {
                    "name": f.name,
                    "zone_id": f.zone_id,
                    "floor_level": f.floor_level,
                    "description": f.description
                } for f in facilities
            ]
    except Exception as e:
        logger.error("tool_error", tool="find_facilities", error=str(e))
        import traceback
        with open("tool_error.txt", "w") as f:
            f.write(traceback.format_exc())
        return {"error": f"Internal database error: {str(e)}"}


async def search_faqs(query: str) -> list:
    """Search the stadium knowledge base for general questions and rules.

    Use this when fans ask about prohibited items, bag policies, alcohol,
    smoking rules, or ticketing issues.

    Args:
        query: A short search keyword (e.g., 'bag', 'alcohol', 'smoking', 'ticket').
    """
    logger.info("tool_called", tool="search_faqs", query=query)
    try:
        async with database._async_session_factory() as session:
            search_pattern = f"%{query}%"
            stmt = select(FAQEntry).where(
                FAQEntry.question.ilike(search_pattern) | FAQEntry.tags.ilike(search_pattern)
            ).limit(3)
            
            result = await session.execute(stmt)
            faqs = list(result.scalars().all())
            
            if not faqs:
                return [{"note": f"No specific FAQ found for '{query}'."}]
                
            return [
                {
                    "question": faq.question,
                    "answer": faq.answer,
                    "category": faq.category
                } for faq in faqs
            ]
    except Exception as e:
        logger.error("tool_error", tool="search_faqs", error=str(e))
        return [{"error": f"Internal database error: {str(e)}"}]


async def get_transport_options() -> list:
    """Get available transportation options to and from the stadium.

    Use this when fans ask how to get to the stadium, parking, or public transit.
    """
    logger.info("tool_called", tool="get_transport_options")
    try:
        async with database._async_session_factory() as session:
            result = await session.execute(select(TransportOption))
            transports = list(result.scalars().all())
            
            return [
                {
                    "name": t.name,
                    "type": t.transport_type,
                    "nearest_gate": t.nearest_gate_id,
                    "walk_minutes": t.estimated_walk_minutes,
                    "schedule": t.schedule_info
                } for t in transports
            ]
    except Exception as e:
        logger.error("tool_error", tool="get_transport_options", error=str(e))
        return [{"error": f"Internal database error: {str(e)}"}]

# Group them in a list for easy import
stadium_tools = [get_zone_status, find_facilities, search_faqs, get_transport_options]
