import requests
from bs4 import BeautifulSoup

url = 'https://www.franksonnenbergonline.com/blog/are-you-grateful/'
response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.text, 'lxml')
title_tag = soup.find('main').find('header').find('h1')
title_text = title_tag.text
img_find = soup.find('img', class_='attachment-post-image')['src']
post_container = soup.find("div", class_="entry-content")
post_text = post_container.get_text(separator="\n")
print(title_text, img_find, post_text, sep='\n')
