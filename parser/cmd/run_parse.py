import argparse
import asyncio
import os

from parser.services.async_parser import parse_hh_vacancies
from parser.services.async_writer import write_to_csv


async def get_args():
    parser = argparse.ArgumentParser(
        description='Parse hh Vacancy and write the result to csv  ',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-q ', '--query',
        default=None,
        help='Vacancy Query, note check for correct format in hh docs. Example : Machine+learning+engineer++ ',
        required=True)
    parser.add_argument(
        '--date_from',
        default=None,
        help='Search vacancy from, must be YYYY-MM-DD')

    parser.add_argument(
        '--date_to',
        default=None,
        help='Search vacancy to , must be YYYY-MM-DD ')

    parser.add_argument(
        '--area',
        default=1,
        help='Search area . Check hh dock , must be int. Default Moscow ')

    parser.add_argument(
        '--filepath',
        default=f'{os.path.abspath(os.sep)}/tmp/hh_vacancy.py',
        help='Filepath. Default is root tmp folder')

    return parser.parse_args()


async def parse():
    args = await get_args()
    res = await parse_hh_vacancies(query=args.query,
                                   date_to=args.date_to,
                                   date_from=args.date_from,
                                   area=args.area)

    await write_to_csv(res=res, file_path=args.filepath)

    print(f"File recorded to {args.filepath}")


def main():
    loop = asyncio.get_event_loop()

    loop.run_until_complete(parse())

    loop.close()


if __name__ == '__main__':
    main()
