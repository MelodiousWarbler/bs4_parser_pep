from bs4 import BeautifulSoup
from exceptions import ParserFindTagException
from requests import RequestException

RESPONSE_ERROR = 'Возникла ошибка при загрузке страницы {url}, {error}'
ERROR_MESSAGE = 'Не найден тег {tag} {attrs}'


def make_soup(session, url, features='lxml'):
    return BeautifulSoup(get_response(session, url).text, features=features)


def get_response(session, url, encoding='utf-8'):
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException as error:
        raise ConnectionError(RESPONSE_ERROR.format(url=url, error=error))


def find_tag(soup, tag, attrs=None):
    attrs_find = {} if attrs is None else attrs
    searched_tag = soup.find(tag, attrs=attrs_find)
    if searched_tag is None:
        raise ParserFindTagException(
            ERROR_MESSAGE.format(tag=tag, attrs=attrs)
        )
    return searched_tag
