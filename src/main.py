import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR, DOWNLOADS_DIR_NAME, MAIN_DOC_URL, PEP_URL, EXPECTED_STATUS
)
from outputs import control_output
from utils import find_tag, make_soup

PROGRAM_MALFUNCTION = 'Сбой в работе программы: {error}'
CAMMAND_ARGS = 'Аргументы командной строки: {args}'
ARCHIVE_SAVE = 'Архив был загружен и сохранён: {archive_path}'
CONNECT_ERR = 'Не удалось подключиться {error} {pep_link}'
PARSER_RUN = 'Парсер запущен!'
PARSER_END = 'Парсер завершил работу.'

STATUS_PEP_NOT_FOUND = (
    'Несовпадающие статусы: '
    '{pep_link} '
    'Статус в карточке: {card_status} '
    'Ожидаемые статусы: {statuses} '
)


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    logs = []
    for section in tqdm(
        find_tag(
            find_tag(
                make_soup(session, whats_new_url),
                'section',
                attrs={'id': 'what-s-new-in-python'}
            ),
            'div', attrs={'class': 'toctree-wrapper'}
        ).find_all(
            'li',
            attrs={'class': 'toctree-l1'}
        )
    ):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        try:
            soup = make_soup(session, version_link)
        except ConnectionError as error:
            logs.append(CONNECT_ERR.format(error=error, pep_link=version_link))
            continue
        results.append((
            version_link,
            find_tag(soup, 'h1').text,
            find_tag(soup, 'dl').text.replace('\n', ' ')
        ))
    for log in logs:
        logging.info(log)
    return results


def latest_versions(session):
    soup = make_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise LookupError('Ничего не нашлось')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (a_tag['href'], version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = make_soup(session, downloads_url)
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag,
        'a',
        attrs={'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / DOWNLOADS_DIR_NAME
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(ARCHIVE_SAVE.format(archive_path=archive_path))


def pep(session):
    pattern_status = r'^Status.*'
    count_statuses = defaultdict(int)
    logs = []
    for tr_tag in tqdm(
        make_soup(session, PEP_URL).select('#numerical-index tbody tr')
    ):
        statuses = EXPECTED_STATUS[find_tag(tr_tag, 'td').text[1:]]
        card_status = ''
        pep_link = urljoin(
            PEP_URL,
            tr_tag.select_one('td a.pep.reference.internal')['href']
        )
        try:
            soup = make_soup(session, pep_link)
        except ConnectionError as error:
            logs.append(CONNECT_ERR.format(error=error, pep_link=pep_link))
            continue
        dt_tags = soup.select_one('dl.rfc2822.field-list.simple').select(
            'dt'
        )
        for dt_tag in dt_tags:
            text_match = re.search(pattern_status, dt_tag.text)
            if text_match:
                card_status = dt_tag.find_next_sibling('dd').text
                break
            else:
                continue
        if card_status not in statuses:
            logs.append(
                STATUS_PEP_NOT_FOUND.format(
                    pep_link=pep_link,
                    card_status=card_status,
                    statuses=statuses
                )
            )
        else:
            count_statuses[card_status] += 1
    for log in logs:
        logging.info(log)
    return [
        ('Статус', 'Количество'),
        *count_statuses.items(),
        ('Total', sum(count_statuses.values())),
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info(PARSER_RUN)
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(CAMMAND_ARGS.format(args=args))
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        results = MODE_TO_FUNCTION[args.mode](session)
        if results is not None:
            control_output(results, args)
    except Exception as error:
        logging.exception(
            PROGRAM_MALFUNCTION.format(error=error),
            stack_info=True
        )
    logging.info(PARSER_END)


if __name__ == '__main__':
    main()
