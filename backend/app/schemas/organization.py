from pydantic import BaseModel


class CompanyBase(BaseModel):
    name: str


class CompanyRead(CompanyBase):
    id: int

    class Config:
        from_attributes = True


class BranchBase(BaseModel):
    company_id: int
    name: str


class BranchRead(BranchBase):
    id: int

    class Config:
        from_attributes = True


class AreaBase(BaseModel):
    name: str


class AreaRead(AreaBase):
    id: int

    class Config:
        from_attributes = True
