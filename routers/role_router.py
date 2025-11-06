# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from core.database import get_db
# from schemas.role_schema import RoleCreate, RoleResponse
# from models.role import Role
# from utils.security import get_current_user
# from models.user import User

# router = APIRouter(prefix="/roles", tags=["Roles"])

# # 🟢 Only Admin can create roles
# @router.post("/", response_model=RoleResponse)
# def create_role(
#     role: RoleCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     # ✅ Restrict access only to admins
#     if current_user.role_name.lower() != "admin":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only admins can create roles"
#         )

#     existing_role = db.query(Role).filter(Role.name == role.name).first()
#     if existing_role:
#         raise HTTPException(status_code=400, detail="Role already exists")

#     db_role = Role(name=role.name)
#     db.add(db_role)
#     db.commit()
#     db.refresh(db_role)
#     return db_role


# # 🟢 Allow only Admin or Manager to view all roles
# @router.get("/", response_model=list[RoleResponse])
# def list_roles(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     # ✅ Restrict to admin or manager
#     if current_user.role_name.lower() not in ["admin", "manager"]:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only admin and manager can view roles"
#         )
#     return db.query(Role).all()
