import requests
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from parse_tululu import parse_book_page, download_image, save_comments, download_txt_with_retry

base_url = "https://tululu.org/l55/"

book_links = []

book_descriptions = []

for page in range(1, 4):
    url = f"{base_url}{page}/"

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    book_cards = soup.find_all('table', class_='d_book')

    for book_card in book_cards:
        book_link = book_card.find('a')['href']
        full_book_link = urljoin(url, book_link)
        book_links.append(full_book_link)

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