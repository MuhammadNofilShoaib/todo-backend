from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_session
from models import Skill, SkillCreate, SkillRead, SkillUpdate, SubAgent
from auth import get_current_user
from typing import List
import uuid

router = APIRouter(prefix="/api/skills", tags=["Skills"])


@router.get("/", response_model=List[SkillRead])
def get_skills(
    sub_agent_id: str = None,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all skills for the current user, optionally filtered by sub-agent."""
    query = session.query(Skill).join(SubAgent).filter(SubAgent.user_id == current_user.id)

    if sub_agent_id:
        try:
            sub_agent_uuid = uuid.UUID(sub_agent_id)
            query = query.filter(Skill.sub_agent_id == sub_agent_uuid)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid sub-agent ID format"
            )

    skills = query.all()
    return skills


@router.post("/", response_model=SkillRead)
def create_skill(
    skill_data: SkillCreate,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new skill for a sub-agent belonging to the current user."""
    # Validate that name is provided
    if not skill_data.name or not skill_data.name.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{"loc": ["body", "name"], "msg": "name is required", "type": "value_error"}]
        )

    # Verify that the sub-agent belongs to the current user
    try:
        sub_agent_uuid = uuid.UUID(skill_data.sub_agent_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid sub-agent ID format"
        )

    sub_agent = session.query(SubAgent).filter(SubAgent.id == sub_agent_uuid, SubAgent.user_id == current_user.id).first()

    if not sub_agent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Sub-agent does not belong to current user"
        )

    # Create new skill
    skill = Skill(
        name=skill_data.name,
        description=skill_data.description,
        sub_agent_id=sub_agent_uuid
    )

    session.add(skill)
    session.commit()
    session.refresh(skill)

    return skill


@router.get("/{skill_id}", response_model=SkillRead)
def get_skill(
    skill_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a specific skill by ID if it belongs to a sub-agent of the current user."""
    try:
        skill_uuid = uuid.UUID(skill_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )

    skill = session.query(Skill).join(SubAgent).filter(
        Skill.id == skill_uuid,
        SubAgent.user_id == current_user.id
    ).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found or access denied"
        )

    return skill


@router.put("/{skill_id}", response_model=SkillRead)
def update_skill(
    skill_id: str,
    skill_data: SkillUpdate,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a specific skill if it belongs to a sub-agent of the current user."""
    try:
        skill_uuid = uuid.UUID(skill_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )

    skill = session.query(Skill).join(SubAgent).filter(
        Skill.id == skill_uuid,
        SubAgent.user_id == current_user.id
    ).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found or access denied"
        )

    # Update skill fields if provided
    if skill_data.name is not None:
        skill.name = skill_data.name
    if skill_data.description is not None:
        skill.description = skill_data.description

    session.add(skill)
    session.commit()
    session.refresh(skill)

    return skill


@router.delete("/{skill_id}")
def delete_skill(
    skill_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a specific skill if it belongs to a sub-agent of the current user."""
    try:
        skill_uuid = uuid.UUID(skill_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )

    skill = session.query(Skill).join(SubAgent).filter(
        Skill.id == skill_uuid,
        SubAgent.user_id == current_user.id
    ).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found or access denied"
        )

    session.delete(skill)
    session.commit()

    return {"message": "Skill deleted successfully"}