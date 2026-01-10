from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel
import uuid


# Pydantic models for request/response validation
class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime


class UserUpdate(BaseModel):
    email: Optional[str] = None


# SQLModel for database
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default=datetime.utcnow())

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="user")
    sub_agents: list["SubAgent"] = Relationship(back_populates="user")


# Task models
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False)
    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    created_at: datetime = Field(default=datetime.utcnow())
    updated_at: datetime = Field(default=datetime.utcnow(), sa_column_kwargs={"onupdate": datetime.utcnow()})

    # Relationship
    user: User = Relationship(back_populates="tasks")


# SubAgent models
class SubAgentBase(BaseModel):
    name: str
    description: Optional[str] = None


class SubAgentCreate(SubAgentBase):
    pass


class SubAgentRead(SubAgentBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class SubAgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class SubAgent(SQLModel, table=True):
    __tablename__ = "sub_agents"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    description: Optional[str] = None
    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    created_at: datetime = Field(default=datetime.utcnow())
    updated_at: datetime = Field(default=datetime.utcnow(), sa_column_kwargs={"onupdate": datetime.utcnow()})

    # Relationship
    user: User = Relationship(back_populates="sub_agents")
    skills: list["Skill"] = Relationship(back_populates="sub_agent")


# Skill models
class SkillBase(BaseModel):
    name: str
    description: Optional[str] = None
    sub_agent_id: uuid.UUID


class SkillCreate(SkillBase):
    pass


class SkillRead(SkillBase):
    id: uuid.UUID
    sub_agent_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Skill(SQLModel, table=True):
    __tablename__ = "skills"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    description: Optional[str] = None
    sub_agent_id: uuid.UUID = Field(foreign_key="sub_agents.id", ondelete="CASCADE")
    created_at: datetime = Field(default=datetime.utcnow())
    updated_at: datetime = Field(default=datetime.utcnow(), sa_column_kwargs={"onupdate": datetime.utcnow()})

    # Relationship
    sub_agent: SubAgent = Relationship(back_populates="skills")