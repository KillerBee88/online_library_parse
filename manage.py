import os
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def download_txt(url, filename, folder='books/'):
    sanitized_filename = sanitize_filename(filename)

    os.makedirs(folder, exist_ok=True)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response = requests.get(url, headers=headers)

    if response.history:
        if response.url.startswith('https://tululu.org/txt.php'):
            raise requests.HTTPError('Redirected to the main page')
    content_type = response.headers.get('Content-Type')
    if not content_type.startswith('text/plain'):
        return None

    filepath = os.path.join(folder, f'{sanitized_filename}.txt')
    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


os.makedirs('books', exist_ok=True)

for book_id in range(1, 11):
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

    txt_url = f'https://tululu.org/txt.php?id={book_id}'
    filename = f'{book_id}_{title}'

    filepath = download_txt(txt_url, filename)