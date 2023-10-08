__all__ = 'VacancyData'
from datetime import datetime

from typing import Optional

from pydantic import BaseModel


class HashableModel(BaseModel):
    """Since I have no intention to change parsed data ,
       lets make object hashable and put it in set
       in order to ensure idempotency """

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class Salary(HashableModel):
    start: Optional[int] = None
    to: Optional[int] = None
    currency: Optional[str] = None


class VacancyData(HashableModel):
    id: int
    vacancy_name: str
    city_name: str
    salary_full: Optional[Salary] = None
    published_at: datetime
    accredited_it_employer: bool
    trusted_employer: bool
    employer_name: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d'),
        }
