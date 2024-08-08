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
    

def extract_section_data(section, json_title=None):
    """
    Extracts data from a given section, ensuring each child section is processed independently,
    and using the appropriate title based on available tags.
    """
    
    # Lấy tiêu đề chính từ thẻ <h2> của phần tử <section> lớn
    h2_tag = section.find('h2')
    h2_title = h2_tag.get_text(strip=True) if h2_tag else ''

    section_data = []
    
    # Xử lý các thẻ <section> con có 'data-testid' là 'topicGHead'
    child_sections = section.find_all('section', attrs={'data-testid': 'topicGHead'})

    if child_sections:
        # Xử lý các section con nếu có
        for child_section in child_sections:
            h3_tags = child_section.find_all('h3')
            h3_titles = [h3.get_text(strip=True) for h3 in h3_tags]

            # Chỉ lấy nội dung <span> con của section này
            span_tags = child_section.find_all('span', attrs={'data-testid': 'topicText'})
            span_contents = [span.get_text(strip=True) for span in span_tags]

            li_tags = child_section.find_all('li', attrs={'data-testid': 'topicListItem'})
            li_contents = [li.get_text(strip=True) for li in li_tags]

            # Ensure each child section has its own unique content row
            if h3_titles:
                for h3_title in h3_titles:
                    title = f"{h2_title} - {h3_title}".strip() if h2_title else h3_title.strip()
                    content = '\n'.join(span_contents + li_contents).strip()
                    if title:
                        section_data.append((title, content))
            else:
                # If no h3, still process content for this section
                title = h2_title.strip() if h2_title else json_title.strip() if json_title else ''
                content = '\n'.join(span_contents + li_contents).strip()
                if title:
                    section_data.append((title, content))
    else:
        # Xử lý nếu không có section con, chỉ có section cha
        h3_tags = section.find_all('h3')
        h3_titles = [h3.get_text(strip=True) for h3 in h3_tags]

        span_tags = section.find_all('span', attrs={'data-testid': 'topicText'})
        span_contents = [span.get_text(strip=True) for span in span_tags]

        li_tags = section.find_all('li', attrs={'data-testid': 'topicListItem'})
        li_contents = [li.get_text(strip=True) for li in li_tags]

        if h3_titles:
            for h3_title in h3_titles:
                title = f"{h2_title} - {h3_title}".strip() if h2_title else h3_title.strip()
                content = '\n'.join(span_contents + li_contents).strip()
                if title:
                    section_data.append((title, content))
        else:
            title = h2_title.strip() if h2_title else json_title.strip() if json_title else ''
            content = '\n'.join(span_contents + li_contents).strip()
            if title:
                section_data.append((title, content))

    # Nếu không có section và không có tiêu đề, dùng tiêu đề JSON
    if not section_data and json_title:
        title = json_title.strip()
        content = '\n'.join(span_contents + li_contents).strip()
        if title:
            section_data.append((title, content))

    return section_data


def scrape_page(url, json_title=None):
    """
    Scrapes content from a webpage given by `url`, using `json_title` as a fallback title.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        sections = soup.find_all('section', attrs={'data-testid': lambda x: x != 'footer'})
        section_data = []

        # Process each top-level section to extract data
        for section in sections:
            section_data.extend(extract_section_data(section, json_title))

        # If no data was collected from sections, attempt to scrape <div> content
        if not section_data:
            divs = soup.find_all('div', attrs={'data-testid': 'topic-main-content'})
            for div in divs:
                spans = div.find_all('span')
                for span in spans:
                    if span.get_text().startswith('Tài liệu tham khảo'):
                        span.decompose()

                for li in div.find_all('li', attrs={'data-testid': 'topicListItem'}):
                    li.decompose()

                h2_tags = div.find_all('h2')
                h2_titles = [h2.get_text(strip=True) for h2 in h2_tags]

                span_tags = div.find_all('span', attrs={'data-testid': 'topicText'})
                span_contents = [span.get_text(strip=True) for span in span_tags]

                li_tags = div.find_all('li', attrs={'data-testid': 'topicListItem'})
                li_contents = [li.get_text(strip=True) for li in li_tags]

                if not h2_titles:
                    # Nếu không có h2, sử dụng tiêu đề từ file JSON nếu có
                    if json_title:
                        title = json_title.strip()
                        content = '\n'.join(span_contents + li_contents).strip()
                        if title:
                            section_data.append((title, content))
                else:
                    for h2_title in h2_titles:
                        title = h2_title.strip()
                        content = '\n'.join(span_contents + li_contents).strip()
                        if title:
                            section_data.append((title, content))

        return section_data

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
        
# Hàm để duyệt dữ liệu và cào thông tin từ các liên kết
def process_data(data, csv_writer):
    for item in data:
        title = item.get("title", item.get("subTitle", ""))
        link = item.get("link")

        print("Title:", title)
        print("Link:", link)

        if "children" not in item or len(item["children"]) == 0:
            sections_data = scrape_page(link)
            if sections_data:
                for section_title, content in sections_data:
                    csv_writer.writerow([section_title, content, link])
                    print("Title:", section_title)
                    print("Content Preview:\n", content[:500])
        else:
            print("Children:")
            process_data(item["children"], csv_writer)
            

# Tạo file CSV và ghi dữ liệu
def save_data_to_csv(data, file_path='../csv/medical.csv'):
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        # Ghi tiêu đề cột
        csv_writer.writerow(['Title', 'Detailed Content', 'Reference Link'])
        # Gọi hàm để xử lý dữ liệu
        process_data(data, csv_writer)
        
# Load JSON data from a file
json_file_path = '../json/listData.json'
json_data = load_json_file(json_file_path)

if json_data:
    # Save scraped data to CSV
    save_data_to_csv(json_data)
else:
    print("Failed to load or process JSON data.")