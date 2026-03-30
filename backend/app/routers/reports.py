from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.report import DashboardMetrics
from app.services.dashboard_service import get_dashboard_metrics

router = APIRouter()


@router.get("/dashboard", response_model=DashboardMetrics)
def dashboard_route(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> DashboardMetrics:
    return DashboardMetrics(**get_dashboard_metrics(db))
