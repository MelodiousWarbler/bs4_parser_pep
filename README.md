# Проект парсинга pep
Включает в себя четыре парсера информации с официального сайта Python:
- получение версий Python с их текущими статусами
- получение перечня нововведений в версиях Python
- скачивание архива последней версии документации Python
- получение количества PEP с их статусами

Парсер включает в себя кеширование результатов запроса.

## Применяемые технологии

[![Python](https://img.shields.io/badge/Python-3.7-blue?style=flat-square&logo=Python&logoColor=3776AB&labelColor=d0d0d0)](https://www.python.org/)
[![Beautiful Soup 4](https://img.shields.io/badge/BeautifulSoup-4.9.3-blue?style=flat-square&labelColor=d0d0d0)](https://beautiful-soup-4.readthedocs.io)

### Подготовка к использованию
- Установите и активируйте виртуальное окружение
- Установите зависимости из файла requirements.txt
`pip install -r requirements.txt`

### Использование
`python main.py [-h] [-c] [-o {pretty,file}] {whats-new,latest-versions,download,pep}`

Программа имеет четыре режима работы:
- whats-new
- latest-versions
- download 
- pep

Доступно три способа вывода информации:
- в консоль без форматирования (без аргументов)
- в консоль с красивым форматированием (аргумент -o pretty)
- в файл в формате .csv (аргумент -o file)

Вызов справки по аргументам командной строки:
`python main.py --help`

## Автор
- [Яков Плакотнюк](https://github.com/MelodiousWarbler "GitHub аккаунт")