from pydantic import BaseModel


class InviteUserRequest(BaseModel):
    space_id: str
    first_name: str
    last_name: str
    email: str
    password: str


class ChangeUserRoleRequest(BaseModel):
    new_role: str
