# Как использовать скрипт для скачивания книг с tululu.org

  

Этот скрипт позволяет скачивать книги с сайта [tululu.org](https://tululu.org/) и сохранять их в формате txt, а также сопутствующие изображения и комментарии.

  

## Установка

  

Для работы скрипта необходимо установить [Python 3.7](https://www.python.org/downloads/) и зависимости, указанные в файле requirements.txt:

  

```

pip install -r requirements.txt

```

  

## Использование

  

+ Для запуска скрипта нужно выполнить команду:
```python parse_tululu.py <start_id> <end_id>```
где `<start_id>` и `<end_id>` - это начальный и конечный идентификаторы книг, которые нужно скачать. Этот скрипт скачивает книги по номерам.
Например, чтобы скачать книги с 3 по 8, нужно выполнить команду:
```python parse_tululu.py 3 8```
После выполнения скрипта книги будут сохранены в папке books, изображения - в папке images, а комментарии - в папке comments.

+ Так же есть еще один скрипт, который скачивает книги по страницам.
Для его использования нужно выполнить команду:
``` python parse_tululu_category.py <start_page> <end_page> ```
где ```<start_page>``` и  ```<end_page>``` - это начальная страница и конечная страница, с которых нужно скачать книги. После выполнения скрипта книги будут сохранены в папке books, изображения - в папке images, а так же будет сохранен файл ```json``` с описанием этих книг.


  

## Опции командной строки

  

+ Скрипт ```parse_tululu.py``` поддерживает следующие опции командной строки:
`start_id` - начальный идентификатор книги (по умолчанию 1)
`end_id` - конечный идентификатор книги (по умолчанию 10)


+ Скрипт  ```parse_tululu_category.py``` поддерживает следующие опции:
```pages``` - это номера страниц. Их можно указывать как в диапазоне, так и одиночно.
```--dest_folder``` - папка в которую нужно сохранить книги, картинки и json. По дефолту они сохраняются в корневую папку.
```--skip_imgs``` - пропустить скачивание картинок.
```--skip_txt``` - пропустить скачивание текста книги.
