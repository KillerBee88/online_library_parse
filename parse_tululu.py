import argparse
import os

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlencode, urlunparse


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError("Страница была перенаправлена")


def parse_book_page(html, book_url):
    soup = BeautifulSoup(html, 'html.parser')

    title_and_author = soup.select_one('h1').text.split('::')
    title = title_and_author[0].strip()
    author = title_and_author[1].strip()

    genre = soup.select_one('span.d_book a').text.strip()

    img_url = soup.select_one('div.bookimage img')['src']
    img_url = urljoin(book_url, img_url)

    book_description = {
        'Name': title,
        'Author': author,
        'Genre': genre,
        'Cover': img_url
    }

    return book_description


def download_txt(txt_url, filename, folder='books'):
    response = requests.get(txt_url)
    try:
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f'Ошибка при выполнении запроса: {e}')
        return

    os.makedirs(folder, exist_ok=True)

    with open(os.path.join(folder, filename), 'w', encoding='utf-8') as file:
        file.write(response.text)



def download_image(img_url, filename, folder='images'):
    response = requests.get(img_url)
    try:
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f'Ошибка при выполнении запроса: {e}')
        return

    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, filename), 'wb') as file:
        file.write(response.content)


def get_comments(html):
    soup = BeautifulSoup(html, 'lxml')
    comments = soup.find_all('div', class_='texts')
    return [comment.get_text(strip=True) for comment in comments]


def save_comments(comments, filename, folder='comments'):
    os.makedirs(folder, exist_ok=True)

    with open(os.path.join(folder, filename), 'w', encoding='utf-8') as file:
        for comment in comments:
            file.write(comment + '\n\n')


def main():
    parser = argparse.ArgumentParser(description='Download books from tululu.org')
    parser.add_argument('start_id', type=int, default=1, help='Start book ID')
    parser.add_argument('end_id', type=int, default=10, help='End book ID')
    args = parser.parse_args()

    start_id = args.start_id
    end_id = args.end_id

    for book_id in range(start_id, end_id + 1):
        book_url = f"https://tululu.org/b{book_id}/"
        response = requests.get(book_url)
        if response is None:
            continue
        
        try:
            check_for_redirect(response)
        except requests.exceptions.HTTPError:
            print(f"Страница {book_url} была перенаправлена")
            continue

        html = response.text
        book_description = parse_book_page(html, book_url)
        if book_description is None:
            print(f"Для книги {book_id} описание не найдено")
            continue
        else:
            print(f"Для книги {book_id} описание получено")

        txt_params = {'id': book_id}
        txt_url = urlunparse(('https', 'tululu.org', '/txt.php', '', urlencode(txt_params), '')) 
        txt_filename = f'{book_id}_{sanitize_filename(book_description["Name"])}.txt'
        img_url = book_description['Cover']
        img_filename = f'{book_id}_{sanitize_filename(book_description["Name"])}.jpg'
        comments_filename = f'{book_id}_{sanitize_filename(book_description["Name"])}.txt'

        comments = get_comments(html)
        if comments:
            print(f"Для книги {book_id} комментарии получены")
            save_comments(comments, comments_filename)
        else:
            print(f"Для книги {book_id} комментариев нет")

        download_txt(txt_url, txt_filename)
        download_image(img_url, img_filename) 


if __name__ == '__main__':
    main()
