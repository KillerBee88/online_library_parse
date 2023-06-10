import os
import requests

os.makedirs('books', exist_ok=True)

for book_id in range(1, 11):
    url = f'https://tululu.org/txt.php?id={book_id}'

    response = requests.get(url)

    if response.status_code == 404:
        continue

    content_type = response.headers.get('Content-Type')
    if not content_type.startswith('text'):
        continue

    filename = f'book_{book_id}.txt'
    filepath = os.path.join('books', filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)