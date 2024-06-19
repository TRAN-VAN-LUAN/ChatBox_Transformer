import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_content_url(url):
    response = requests.get(url)
    response.raise_for_status()  # Kiểm tra lỗi HTTP
    return response.content

def get_articles_links_from_subtopic(url: str, subtopic: str) -> list:
    links = []
    content = get_content_url(url)  # Hàm get_content_url(url) chưa được định nghĩa trong phạm vi này
    soup = BeautifulSoup(content, 'html.parser')
    articles = soup.find_all('table')

    latest_title = ''  # Biến lưu trữ title mới nhất

    for article in articles:
        divs = article.find_all('div', class_='content1')
        for div in divs:
            rows = div.find_all('p')
            for row in rows:
                title = ''
                content = ''

                # Kiểm tra nếu thẻ <a> có trong thẻ <p>
                a_tag = row.find('a')
                if a_tag:
                    if a_tag.has_attr('name'):
                        name_value = a_tag['name']
                        if name_value.startswith('dieu_') or name_value.startswith('chuong_') or name_value.startswith('muc_'):
                            title = a_tag.get_text(strip=True)
                            latest_title = title  # Cập nhật title mới nhất
                            content = row.get_text(strip=True).replace(title, '').strip()

                if not title:  
                    title = latest_title  # Sử dụng title mới nhất nếu không có thẻ <a>
                    content = row.get_text(strip=True)

                links.append({'title': title, 'content': content, 'subtopic': subtopic})
    
    return links

# Sử dụng hàm
url = "https://thuvienphapluat.vn/van-ban/Bat-dong-san/Luat-Dat-dai-2024-31-2024-QH15-523642.aspx"
subtopic = "Luat-Dat-dai-2024"
links = get_articles_links_from_subtopic(url, subtopic)

# Lưu dữ liệu thành file txt
with open('data/txt/articles.txt', 'w', encoding='utf-8') as file:
    for link in links:
        file.write(f"Title: {link['title']}\n")
        file.write(f"Content: {link['content']}\n")
        file.write(f"SubTopic: {link['subtopic']}\n")
        file.write("\n")

# Lưu dữ liệu thành DataFrame và xuất ra file CSV
df = pd.DataFrame(links)
df.to_csv('data/csv/articles.csv', index=False, encoding='utf-8')


print("Dữ liệu đã được lưu thành file txt, csv và xlsx.")