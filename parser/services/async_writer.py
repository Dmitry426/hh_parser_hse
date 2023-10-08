__all__ = 'write_to_csv'

import csv
import os

import aiofiles
from aiocsv import AsyncDictWriter

PATH = os.path.abspath('')


async def write_to_csv(res, file_path: str = f"{PATH}/vacancies.csv"):
    """Create CSV asynchronously """
    async with aiofiles.open(file_path, mode="w", encoding="utf-8", newline="") as afp:
        writer = AsyncDictWriter(afp, fieldnames=next(iter(res)).model_dump().keys(),
                                 restval="NULL",
                                 quoting=csv.QUOTE_ALL)

        await writer.writeheader()
        await writer.writerows([model.model_dump() for model in res])
