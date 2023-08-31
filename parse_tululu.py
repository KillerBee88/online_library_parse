import argparse
import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


class ParsingError(Exception):
    pass


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError("Страница была перенаправлена")


def parse_book_page(html, book_url):
    soup = BeautifulSoup(html, 'html.parser')

    title_and_author = soup.select_one('h1').text.split('::')
    title = title_and_author[0].strip()
    author = title_and_author[1].strip()

    genre = soup.select_one('span.d_book a').text.strip()

    img_url = urljoin(book_url, soup.select_one('div.bookimage img')['src'])

    comments = [comment.get_text(strip=True) for comment in soup.find_all('div', class_='texts')]

    return {
        'Name': title,
        'Author': author,
        'Genre': genre,
        'Cover': img_url,
        'Comments': comments
    }


def download_image(img_url, filename, folder='images'):
    response = requests.get(img_url)
    response.raise_for_status()
    
    os.makedirs(folder, exist_ok=True)
    
    with open(os.path.join(folder, filename), 'wb') as file:
        file.write(response.content)


def save_comments(comments, filename, folder='comments'):
    os.makedirs(folder, exist_ok=True)
    
    with open(os.path.join(folder, filename), 'w', encoding='utf-8') as file:
        file.writelines(comment + '\n\n' for comment in comments)
        

def download_txt_with_retry(txt_url, filename, params=None, folder='books', max_retries=3, retry_delay=5):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(txt_url, params=params)
            response.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            print(f'Ошибка при выполнении запроса: {e}', file=sys.stderr)
            print(f'Повторная попытка ({retries + 1}/{max_retries}) через {retry_delay} секунд...')
            time.sleep(retry_delay)
            retries += 1
    else:
        print(f'Не удалось установить соединение с сервером для {filename}', file=sys.stderr)
        return False

    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, filename), 'w', encoding='utf-8') as file:
        file.write(response.text)
    return True


def main():
    parser = argparse.ArgumentParser(description='Download books from tululu.org')
    parser.add_argument('start_id', type=int, default=1, help='Start book ID')
    parser.add_argument('end_id', type=int, default=10, help='End book ID')
    args = parser.parse_args()

    start_id = args.start_id
    end_id = args.end_id

    for book_id in range(start_id, end_id + 1):
        book_url = f"https://tululu.org/b{book_id}/"
        try:
            response = requests.get(book_url)
            check_for_redirect(response)
            response.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            print(f"Ошибка при выполнении запроса для книги {book_id}: {e}", file=sys.stderr)
            time.sleep(5)
            continue

        html = response.text
        book_description = parse_book_page(html, book_url)

        img_url = book_description['Cover']
        txt_url = 'https://tululu.org/txt.php'
        txt_params = {'id': book_id}
        sanitized_name = sanitize_filename(book_description["Name"])
        txt_filename = f'{book_id}_{sanitized_name}.txt'
        img_filename = f'{book_id}_{sanitized_name}.jpg'
        comments_filename = f'{book_id}_{sanitized_name}.txt'

        try:
            response = download_txt_with_retry(txt_url, txt_filename, txt_params)
            download_image(img_url, img_filename)
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            print(f'Ошибка при выполнении запроса для книги {book_id}: {e}', file=sys.stderr)
            time.sleep(5)
            continue

        comments = book_description.get('Comments')
        if comments:
            print(f"Для книги {book_id} комментарии получены")

        try:
            save_comments(comments, comments_filename)
        except OSError as e:
            print(f'Ошибка при сохранении комментариев для книги {book_id}: {e}', file=sys.stderr)
            continue
        else:
            print(f"Для книги {book_id} комментариев нет")


if __name__ == '__main__':
    main()