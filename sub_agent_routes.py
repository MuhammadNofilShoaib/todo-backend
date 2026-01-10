from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_session
from models import SubAgent, SubAgentCreate, SubAgentRead, SubAgentUpdate
from auth import get_current_user
from typing import List
import uuid

router = APIRouter(prefix="/api/sub-agents", tags=["Sub-Agents"])


@router.get("/", response_model=List[SubAgentRead])
def get_sub_agents(
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all sub-agents for the current user."""
    sub_agents = session.query(SubAgent).filter(SubAgent.user_id == current_user.id).all()
    return sub_agents


@router.post("/", response_model=SubAgentRead)
def create_sub_agent(
    sub_agent_data: SubAgentCreate,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new sub-agent for the current user."""
    # Validate that name is provided
    if not sub_agent_data.name or not sub_agent_data.name.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{"loc": ["body", "name"], "msg": "name is required", "type": "value_error"}]
        )

    # Create new sub-agent with current user's ID
    sub_agent = SubAgent(
        name=sub_agent_data.name,
        description=sub_agent_data.description,
        user_id=current_user.id
    )

    session.add(sub_agent)
    session.commit()
    session.refresh(sub_agent)

    return sub_agent


@router.get("/{sub_agent_id}", response_model=SubAgentRead)
def get_sub_agent(
    sub_agent_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a specific sub-agent by ID if it belongs to the current user."""
    try:
        sub_agent_uuid = uuid.UUID(sub_agent_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sub-agent not found"
        )

    sub_agent = session.query(SubAgent).filter(SubAgent.id == sub_agent_uuid, SubAgent.user_id == current_user.id).first()

    if not sub_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sub-agent not found or access denied"
        )

    return sub_agent


@router.put("/{sub_agent_id}", response_model=SubAgentRead)
def update_sub_agent(
    sub_agent_id: str,
    sub_agent_data: SubAgentUpdate,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a specific sub-agent if it belongs to the current user."""
    try:
        sub_agent_uuid = uuid.UUID(sub_agent_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sub-agent not found"
        )

    sub_agent = session.query(SubAgent).filter(SubAgent.id == sub_agent_uuid, SubAgent.user_id == current_user.id).first()

    if not sub_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sub-agent not found or access denied"
        )

    # Update sub-agent fields if provided
    if sub_agent_data.name is not None:
        sub_agent.name = sub_agent_data.name
    if sub_agent_data.description is not None:
        sub_agent.description = sub_agent_data.description

    session.add(sub_agent)
    session.commit()
    session.refresh(sub_agent)

    return sub_agent


@router.delete("/{sub_agent_id}")
def delete_sub_agent(
    sub_agent_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a specific sub-agent if it belongs to the current user."""
    try:
        sub_agent_uuid = uuid.UUID(sub_agent_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sub-agent not found"
        )

    sub_agent = session.query(SubAgent).filter(SubAgent.id == sub_agent_uuid, SubAgent.user_id == current_user.id).first()

    if not sub_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sub-agent not found or access denied"
        )

    session.delete(sub_agent)
    session.commit()

    return {"message": "Sub-agent deleted successfully"}