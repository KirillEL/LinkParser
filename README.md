# Web Crawler / Word Indexer

## Описание

Парсер, который, начиная с заданного URL-адреса, рекурсивно проходит по всем доступным ссылкам и сохраняет слова, найденные на страницах, в базу данных. Скрипт `main.py` запускает процесс парсинга и записи данных.

### Основные функции:
- Рекурсивный обход всех доступных ссылок.
- Сохранение всех найденных слов, а также другой информации (например, метаданных) в базу данных SQLite.
- Возможность настройки глубины парсинга.

## Установка

1. Poetry [Poetry](https://python-poetry.org/). Если нет, установите его:

2. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/KirillEL/LinkParser.git
   ```

3. Установить зависимости:

   ```bash
   poetry install
   ```

4. Активировать виртуальное окружение:

  ```bash
   poetry shell
   ```
   

## Использование

1. Для запуска необходимо выполнить:
   
  ```bash
  poetry run python main.py
  ```

2. Введите url адрес:

   ```bash
   Введите URL для парсинга: https://example.com
   ```
  
