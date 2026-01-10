from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_session
from models import Task, TaskCreate, TaskRead, TaskUpdate
from auth import get_current_user
from typing import List
import uuid

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.get("/", response_model=List[TaskRead])
def get_tasks(
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all tasks for the current user."""
    tasks = session.query(Task).filter(Task.user_id == current_user.id).all()
    return tasks


@router.post("/", response_model=TaskRead)
def create_task(
    task_data: TaskCreate,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new task for the current user."""
    # Validate that title is provided
    if not task_data.title or not task_data.title.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{"loc": ["body", "title"], "msg": "title is required", "type": "value_error"}]
        )

    # Create new task with current user's ID
    task = Task(
        title=task_data.title,
        description=task_data.description,
        completed=task_data.completed if task_data.completed is not None else False,
        user_id=current_user.id
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a specific task by ID if it belongs to the current user."""
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task = session.query(Task).filter(Task.id == task_uuid, Task.user_id == current_user.id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    return task


@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a specific task if it belongs to the current user."""
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task = session.query(Task).filter(Task.id == task_uuid, Task.user_id == current_user.id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    # Update task fields if provided
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.completed is not None:
        task.completed = task_data.completed

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: str,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a specific task if it belongs to the current user."""
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task = session.query(Task).filter(Task.id == task_uuid, Task.user_id == current_user.id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    session.delete(task)
    session.commit()

    return {"message": "Task deleted successfully"}


@router.patch("/{task_id}/complete", response_model=TaskRead)
def toggle_task_completion(
    task_id: str,
    completed: bool,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Toggle completion status of a specific task if it belongs to the current user."""
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task = session.query(Task).filter(Task.id == task_uuid, Task.user_id == current_user.id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    task.completed = completed

    session.add(task)
    session.commit()
    session.refresh(task)

    return task