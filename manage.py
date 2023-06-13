import argparse
import os

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


def get_book_page(book_url):
    response = requests.get(book_url)
    response.raise_for_status()
    return response.text


def parse_book_page(book_url):
    response = requests.get(book_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    book_info_container = soup.find('div', id='content')

    title_and_author = book_info_container.find('h1').get_text(strip=True)
    title, author = map(str.strip, title_and_author.split('::'))

    genre = book_info_container.find('span', class_='d_book').find('a').get_text(strip=True)

    book_data = {
        'Название': title,
        'Автор': author,
        'Жанр': genre,
    }

    return book_data


def get_book_genre(book_id):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    genre = soup.find('span', class_='d_book').find('a').get_text(strip=True)

    return genre


def download_txt(txt_url, filename, folder='books'):
    response = requests.get(txt_url, allow_redirects=False)
    response.raise_for_status()

    os.makedirs(folder, exist_ok=True)

    with open(os.path.join(folder, filename), 'w') as file:
        file.write(response.text)


def download_image(img_url, filename, folder='images'):
    response = requests.get(img_url, allow_redirects=False)
    response.raise_for_status()

    os.makedirs(folder, exist_ok=True)

    with open(os.path.join(folder, filename), 'wb') as file:
        file.write(response.content)


def download_comments(book_id, filename, folder='comments'):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    comments = soup.find_all('div', class_='texts')

    os.makedirs(folder, exist_ok=True)

    with open(os.path.join(folder, filename), 'w') as file:
        for comment in comments:
            file.write(comment.get_text(strip=True) + '\n\n')


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

        soup = BeautifulSoup(response.text, "lxml")
        title_and_author = soup.find("h1").text
        split_title_and_author = title_and_author.split("::")

        if len(split_title_and_author) == 1:
            continue

        title, author = split_title_and_author
        title = title.strip()
        author = author.strip()
        genre = get_book_genre(book_id)

        txt_url = f'https://tululu.org/txt.php?id={book_id}'
        txt_filename = f'{book_id}_{sanitize_filename(title)}.txt'
        img_url = urljoin(book_url, soup.find('div', class_='bookimage').find('img')['src'])
        img_filename = f'{book_id}_{sanitize_filename(title)}.jpg'
        comments_filename = f'{book_id}_{sanitize_filename(title)}.txt'

        book_data = parse_book_page(book_url)

        download_comments(book_id, comments_filename)
        download_txt(txt_url, txt_filename)
        download_image(img_url, img_filename)
        print(book_data)


if __name__ == '__main__':
    main()
