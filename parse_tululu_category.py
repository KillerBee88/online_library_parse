import argparse
import requests
import json
import time
import sys
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from parse_tululu import parse_book_page, download_image, save_comments, download_txt_with_retry, check_for_redirect
import os

base_url = "https://tululu.org/l55/"
httpstat_url = "http://httpstat.us/"

def parse_args():
    parser = argparse.ArgumentParser(description='Скачивание книг с tululu.org')
    parser.add_argument('pages', type=int, nargs='+', help='Номера страниц')
    parser.add_argument('--dest_folder', help='Путь к каталогу для сохранения')
    parser.add_argument('--skip_imgs', action='store_true', help='Не загружать изображения')
    parser.add_argument('--skip_txt', action='store_true', help='Не загружать книги')
    return parser.parse_args()


def check_network_status():
    try:
        response = requests.get(httpstat_url)
        response.raise_for_status()
        return True
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
        return False
    

def main():
    args = parse_args()
    pages = args.pages
    dest_folder = args.dest_folder
    skip_imgs = args.skip_imgs
    skip_txt = args.skip_txt

    book_links = []
    book_descriptions = []

    for page in pages:
        url = f"{base_url}{page}/"

        if not check_network_status():
            print("Ошибка сети. Проверьте подключение к интернету.", file=sys.stderr)
            return

        response = requests.get(url)
        check_for_redirect(response)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        book_cards = soup.select('table.d_book')

        for book_card in book_cards:
            book_link = urljoin(url, book_card.select_one('a')['href'])
            book_links.append(book_link)

    for book_link in book_links:
        if not check_network_status():
            print("Ошибка сети. Проверьте подключение к интернету.", file=sys.stderr)
            continue

        response = requests.get(book_link)
        check_for_redirect(response)
        response.raise_for_status()
        html = response.text
        book_description = parse_book_page(html, book_link)
        book_descriptions.append(book_description)
        book_name = book_description['Name']
        valid_filename = re.sub(r'[\\/*?:"<>|]', '', book_name)
        
        if dest_folder and not skip_imgs:
            book_cover = download_image(book_description['Cover'], f'{valid_filename}.jpg', dest_folder)
        
        if dest_folder and not skip_txt:
            book_id = re.search(r'\d+', book_link).group()
            book_text = download_txt_with_retry(f'https://tululu.org/txt.php?id={book_id}', f'{valid_filename}.txt', dest_folder)

        time.sleep(1)
    
    dest_file = os.path.join(dest_folder, 'book_descriptions.json') if dest_folder else 'book_descriptions.json'

    with open(dest_file, 'w', encoding='utf-8') as file:
        json.dump(book_descriptions, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()