from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    total_vacancies: int
    open_vacancies: int
    total_applications: int
    recommended_applications: int
