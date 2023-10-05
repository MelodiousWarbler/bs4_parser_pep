import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (
    BASE_DIR, DATETIME_FORMAT, FILE_ARG_NAME,
    PRETTY_ARG_NAME, RESULTS_DIR_NAME
)

LOG_MASSAGE = 'Файл с результатами был сохранён: {file_path}'


def default_output(results, *args):
    for row in results:
        print(*row)


def pretty_output(results, *args):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    results_dir = BASE_DIR / RESULTS_DIR_NAME
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect=csv.unix_dialect)
        writer.writerows(results)
    logging.info(LOG_MASSAGE.format(file_path=file_path))


CASES_OUTPUT = {
    PRETTY_ARG_NAME: pretty_output,
    FILE_ARG_NAME: file_output,
    None: default_output,
}


def control_output(results, cli_args):
    CASES_OUTPUT.get(cli_args.output)(results, cli_args)
