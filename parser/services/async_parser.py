__all__ = 'parse_hh_vacancies'

import asyncio
import logging
from typing import Union

import aiohttp
import backoff
from aiohttp import ClientOSError, ClientSession, ServerDisconnectedError

from parser.models.vacancy import Salary, VacancyData

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "api-test-agent"
}


def form_url(query: Union[str, dict],
             date_from: str = None,
             date_to: str = None,
             page: int = 0,
             per_page: int = 100,
             area: int = None) -> str:
    url = (f'https://api.hh.ru/vacancies?'
           f'text={query}&'
           )

    if per_page:
        url += f"&per_page={per_page}"
    if page:
        url += f'&page={page}'
    if area:
        url += f"&area={area}"
    if date_to:
        url += f"&date_to={date_to}"
    if date_from:
        url += f"&date_from={date_from}"

    return url


@backoff.on_exception(backoff.expo,
                      (ServerDisconnectedError, ClientOSError),
                      max_time=10,
                      max_tries=2
                      )
async def get_pagination_number(session: ClientSession, url: str) -> int:
    """Get the number of paginated """
    async with session.get(url, headers=HEADERS) as resp:
        try:
            text = await resp.json()
            return text['pages']
        except KeyError as err:
            logger.error(f"Response has no pagination {err}")


@backoff.on_exception(backoff.expo,
                      (ServerDisconnectedError, ClientOSError),
                      max_time=10,
                      max_tries=2
                      )
async def parse_vacancy(session: ClientSession, url: str) -> set[VacancyData]:
    res = set()
    async with session.get(url, headers=HEADERS) as resp:
        data = await resp.json()
        for item in data['items']:
            salary = None
            if item['salary']:
                salary = Salary(start=item['salary']['from'],
                                to=item['salary']['to'],
                                currency=item['salary']['currency'])

            vacancy = VacancyData(id=item['id'],
                                  vacancy_name=item['name'],
                                  city_name=item['area']['name'],
                                  salary_full=salary if salary else None,
                                  published_at=item['published_at'],
                                  accredited_it_employer=item['employer']['accredited_it_employer'],
                                  trusted_employer=item['employer']['trusted'],
                                  employer_name=item['employer']['name'])

            res.add(vacancy)
        return res


async def parse_hh_vacancies(query: str,
                             date_from: str = None,
                             date_to: str = None,
                             area: int = None) -> set[VacancyData]:
    """Parse vacancies """
    vacancies = []
    async with aiohttp.ClientSession() as session:
        url = form_url(query=query, date_from=date_from, date_to=date_to, area=area)
        pages = await get_pagination_number(session=session, url=url)

        for page in range(0, pages):
            url = form_url(query=query, date_from=date_from, date_to=date_to, page=page, area=area)
            task = asyncio.create_task(parse_vacancy(session=session,
                                                     url=url))
            vacancies.append(task)
        gathered_news = await asyncio.gather(*vacancies)
        res = {item for sublist in gathered_news for item in sublist}
    return res


