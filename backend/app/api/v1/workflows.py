"""
Workflow endpoints
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.workflow import Workflow
from app.models.user import User
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate, WorkflowResponse
from app.dependencies import get_current_user
from app.core.exceptions import NotFoundException

router = APIRouter()


@router.get("", response_model=List[WorkflowResponse])
async def list_workflows(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List user's workflows
    """
    result = await db.execute(
        select(Workflow).where(Workflow.user_id == current_user.id)
        .order_by(Workflow.created_at.desc())
    )
    workflows = result.scalars().all()

    return workflows


@router.post("", response_model=WorkflowResponse)
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new workflow
    """
    workflow = Workflow(
        user_id=current_user.id,
        name=workflow_data.name,
        trigger_type=workflow_data.trigger_type,
        trigger_config=workflow_data.trigger_config,
        actions=workflow_data.actions,
        conditions=workflow_data.conditions
    )

    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)

    return workflow


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get workflow details
    """
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.user_id == current_user.id
        )
    )
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise NotFoundException("Workflow not found")

    return workflow


@router.patch("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    workflow_update: WorkflowUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update workflow
    """
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.user_id == current_user.id
        )
    )
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise NotFoundException("Workflow not found")

    # Update fields
    if workflow_update.name is not None:
        workflow.name = workflow_update.name
    if workflow_update.status is not None:
        workflow.status = workflow_update.status
    if workflow_update.trigger_config is not None:
        workflow.trigger_config = workflow_update.trigger_config
    if workflow_update.actions is not None:
        workflow.actions = workflow_update.actions
    if workflow_update.conditions is not None:
        workflow.conditions = workflow_update.conditions

    await db.commit()
    await db.refresh(workflow)

    return workflow


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete workflow
    """
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.user_id == current_user.id
        )
    )
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise NotFoundException("Workflow not found")

    await db.delete(workflow)
    await db.commit()

    return {"message": "Workflow deleted successfully"}
