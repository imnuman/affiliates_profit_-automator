"""
Workflow schemas
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, UUID4


class WorkflowBase(BaseModel):
    """Base workflow schema"""
    name: str
    trigger_type: str
    actions: List[Dict[str, Any]]


class WorkflowCreate(WorkflowBase):
    """Workflow creation schema"""
    trigger_config: Optional[Dict[str, Any]] = None
    conditions: Optional[Dict[str, Any]] = None


class WorkflowUpdate(BaseModel):
    """Workflow update schema"""
    name: Optional[str] = None
    status: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    conditions: Optional[Dict[str, Any]] = None


class WorkflowResponse(WorkflowBase):
    """Workflow response schema"""
    id: UUID4
    user_id: UUID4
    status: str
    trigger_config: Optional[Dict[str, Any]] = None
    conditions: Optional[Dict[str, Any]] = None
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
