import argparse
import os
import sys
import time

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


def check_for_redirect(response, url):
    if response.url != url:
        print(f'Страница {url} не найдена')
        return False
    return True


def make_request(url):
    while True:
        try:
            response = requests.get(url, allow_redirects=False)
            response.raise_for_status()
            return response
        except requests.exceptions.ConnectionError as e:
            time.sleep(5)
            continue


def parse_book_page(book_url):
    response = make_request(book_url)
    try:
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f'Error while making request: {e}')
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    title_and_author = soup.select_one('h1').text.split('::')
    title = title_and_author[0].strip()
    author = title_and_author[1].strip()

    genre = soup.select_one('span.d_book a').text.strip()

    img_url = soup.select_one('div.bookimage img')['src']
    img_url = urljoin(book_url, img_url)

    book_info = {
        'Название': title,
        'Автор': author,
        'Жанр': genre,
        'Обложка': img_url
    }

    return book_info


def download_txt(txt_url, filename, folder='books'):
    response = make_request(txt_url)
    try:
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f'Error while making request: {e}')
        return

    os.makedirs(folder, exist_ok=True)

    with open(os.path.join(folder, filename), 'w', encoding='utf-8') as file:
        file.write(response.text)



def download_image(img_url, filename, folder='images'):
    response = make_request(img_url)
    try:
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f'Error while making request: {e}')
        return

    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, filename), 'wb') as file:
        file.write(response.content)


def get_comments(book_id):
    url = f'https://tululu.org/b{book_id}/'
    response = make_request(url)
    try:
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f'Error while making request: {e}')
        return []

    soup = BeautifulSoup(response.text, 'lxml')
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
        if not check_for_redirect(response, book_url):
            continue
        
        book_info = parse_book_page(book_url)
        if book_info is None:
            continue

        txt_url = f'https://tululu.org/txt.php?id={book_id}'
        txt_filename = f'{book_id}_{sanitize_filename(book_info["Название"])}.txt'
        img_url = book_info['Обложка']
        img_filename = f'{book_id}_{sanitize_filename(book_info["Название"])}.jpg'
        comments_filename = f'{book_id}_{sanitize_filename(book_info["Название"])}.txt'

        comments = get_comments(book_id)
        if comments:
            save_comments(comments, comments_filename)

        download_txt(txt_url, txt_filename)
        download_image(img_url, img_filename) 


if __name__ == '__main__':
    main()
