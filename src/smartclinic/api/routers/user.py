from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from smartclinic.api.dependencies import get_db
from smartclinic.api.deps_auth import CurrentUser, require_roles
from smartclinic.core.user.user_dto import UpdateUserRoleDTO, UserDTO
from smartclinic.core.user.user_service import get_all_users, update_user_role

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("/", response_model=list[UserDTO])
def list_users(
    _admin: Annotated[CurrentUser, Depends(require_roles("admin"))],
    db: Annotated[Session, Depends(get_db)],
):
    return get_all_users(db)


@router.put("/{user_id}/role", response_model=UserDTO)
def change_user_role(
    user_id: str,
    role_update: UpdateUserRoleDTO,
    _admin: Annotated[CurrentUser, Depends(require_roles("admin"))],
    db: Annotated[Session, Depends(get_db)],
):
    try:
        user = update_user_role(user_id, role_update.role, db)
        return UserDTO(
            id=user.id, user_name=user.user_name, email=user.email, role=user.role
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
