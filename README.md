# eos

## Описание
Данный скрипт используется для сбора информации End Of Sale с сайта cisco

## Требования
  Python 3 + пакеты описанные в файле requirements.txt

## Структура
  Основные 2 скрипта 
  - generate_db.py - используется для сбора информации с сайта циско и сохранения ее в базе sqlite db/eos.db
  - web.py -  веб форма, написанная с использованием flask для отображения информации по eos и ее добавлению/изменению


## База данных
  - Сама база хранится в db/eos.db
  - Схема базы данных описана в db/schema.py
  - Для создания пустой базы данных необходимо использовать скрипт db/create_tables.py (запускать из папки db)
  
## Алгоритм работы generate_db.py
1. Сбор EOS документов из раздела Products
2. Сбор EOS документов из раздела Support
3. Обработка собранных eos докуметов и сохранение ее в базе




