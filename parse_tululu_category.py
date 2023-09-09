import argparse
import requests
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from parse_tululu import parse_book_page, download_image, save_comments, download_txt_with_retry

base_url = "https://tululu.org/l55/"

def parse_args():
    parser = argparse.ArgumentParser(description='Download books from tululu.org')
    parser.add_argument('pages', type=int, nargs='+', help='Page numbers')
    return parser.parse_args()

def main():
    args = parse_args()
    pages = args.pages

    book_links = []
    book_descriptions = []

    for page in pages:
        url = f"{base_url}{page}/"

        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        book_cards = soup.select('table.d_book')

        for book_card in book_cards:
            book_link = urljoin(url, book_card.select_one('a')['href'])
            book_links.append(book_link)

    for book_link in book_links:
        response = requests.get(book_link)
        response.raise_for_status()
        html = response.text
        book_description = parse_book_page(html, book_link)
        book_descriptions.append(book_description)
        book_name = book_description['Name']
        valid_filename = re.sub(r'[\\/*?:"<>|]', '', book_name)
        book_cover = download_image(book_description['Cover'], valid_filename + '.jpg')
        book_id = re.search(r'\d+', book_link).group()
        book_text = download_txt_with_retry(f'https://tululu.org/txt.php?id={book_id}', valid_filename + '.txt')

    with open('book_descriptions.json', 'w', encoding='utf-8') as file:
        json.dump(book_descriptions, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()