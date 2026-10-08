from pydantic import BaseModel


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    space_name: str
    space_address: str
    utility_unit_number: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
