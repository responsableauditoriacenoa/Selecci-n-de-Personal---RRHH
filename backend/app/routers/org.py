from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.organization import Area, Branch, Company
from app.models.user import User
from app.schemas.organization import AreaBase, AreaRead, BranchBase, BranchRead, CompanyBase, CompanyRead

router = APIRouter()


@router.get("/companies", response_model=list[CompanyRead])
def list_companies(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[Company]:
    return db.scalars(select(Company).order_by(Company.id.desc())).all()


@router.post("/companies", response_model=CompanyRead)
def create_company(payload: CompanyBase, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> Company:
    item = Company(name=payload.name)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/branches", response_model=list[BranchRead])
def list_branches(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[Branch]:
    return db.scalars(select(Branch).order_by(Branch.id.desc())).all()


@router.post("/branches", response_model=BranchRead)
def create_branch(payload: BranchBase, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> Branch:
    item = Branch(company_id=payload.company_id, name=payload.name)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/areas", response_model=list[AreaRead])
def list_areas(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[Area]:
    return db.scalars(select(Area).order_by(Area.id.desc())).all()


@router.post("/areas", response_model=AreaRead)
def create_area(payload: AreaBase, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> Area:
    item = Area(name=payload.name)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
