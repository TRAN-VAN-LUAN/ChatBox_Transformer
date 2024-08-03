import os
import json
import requests
from bs4 import BeautifulSoup
import csv

# Load dữ liệu JSON từ file
def load_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

# Hàm để lấy nội dung từ một URL, bỏ qua các section và li không mong muốn
def scrape_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Lấy tất cả các thẻ <section> trừ những thẻ có data-testid là 'footer'
        sections = soup.find_all('section', attrs={'data-testid': lambda x: x != 'footer'})
        section_texts = []

        # Gộp xử lý cho cả <section> và <div>
        for element in sections + soup.find_all('div', attrs={'data-testid': 'topic-main-content'}):
            # Xử lý các thẻ <span> có nội dung bắt đầu với 'Tài liệu tham khảo'
            spans = element.find_all('span')
            for span in spans:
                if span.get_text().startswith('Tài liệu tham khảo'):
                    span.decompose()  # Loại bỏ <span> không mong muốn

            # Bỏ qua các thẻ <li> có data-testid là 'topicListItem' trong phần tử này
            for li in element.find_all('li', attrs={'data-testid': 'topicListItem'}):
                li.decompose()  # Loại bỏ <li> không mong muốn

            # Lấy nội dung từ các phần tử <section> hoặc <div> mà không lặp lại nội dung
            element_text = element.get_text(separator='\n', strip=True)
            section_texts.append(element_text)

        # Kết hợp tất cả các nội dung từ các thẻ <section> và <div>
        all_text = '\n\n'.join(section_texts)
        return all_text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Hàm để duyệt dữ liệu và cào thông tin từ các liên kết
def process_data(data, csv_writer):
    for item in data:
        # Lấy tiêu đề từ "title" hoặc "subTitle"
        title = item.get("title", item.get("subTitle"))
        link = item.get("link")
        
        print("Title:", title)
        print("Link:", link)
        
        # Kiểm tra nếu mục không có children, mới gọi scrape_page
        if "children" not in item or len(item["children"]) == 0:
            content = scrape_page(link)
            if content:
                # Ghi tiêu đề, nội dung và link vào file CSV
                csv_writer.writerow([title, content, link])
                print("Content Preview:\n", content[:500])  # In ra 500 ký tự đầu tiên của nội dung
        else:
            # Nếu có children, tiếp tục duyệt qua các children
            print("Children:")
            process_data(item["children"], csv_writer)

# Tạo file CSV và ghi dữ liệu
def save_data_to_csv(data, file_path='output2.csv'):
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        # Ghi tiêu đề cột
        csv_writer.writerow(['Title', 'Content', 'Link'])
        # Gọi hàm để xử lý dữ liệu
        process_data(data, csv_writer)
        
# Load JSON data from a file
json_file_path = '../listData.json'
json_data = load_json_file(json_file_path)

if json_data:
    # Save scraped data to CSV
    save_data_to_csv(json_data)
else:
    print("Failed to load or process JSON data.")