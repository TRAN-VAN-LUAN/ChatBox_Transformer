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

def extract_innermost_section(section, parent_title, json_title=None):
    """
    Trích xuất dữ liệu từ phần nhỏ nhất (innermost section),
    chỉ xử lý các phần không chứa phần con.
    """
    # Tìm các phần tử <section> con
    child_sections = section.find_all('section')

    # Nếu không có phần con, xử lý phần hiện tại
    if not child_sections:
        return process_child_section(section, parent_title, json_title=json_title)

    # Nếu có phần con, đệ quy để tìm phần nhỏ nhất
    innermost_data = []
    for child_section in child_sections:
        innermost_data.extend(extract_innermost_section(child_section, parent_title, json_title=json_title))

    return innermost_data

def extract_section_data(section, json_title=None):
    """
    Trích xuất dữ liệu từ một phần (section) cụ thể, đảm bảo chỉ xử lý phần nhỏ nhất và gán đúng tiêu đề.
    """
    section_data = []

    # Lấy tiêu đề chính từ thẻ <h2> của phần tử <section> lớn
    h2_tag = section.find('h2')
    if h2_tag:
        span_tag = h2_tag.find('span', attrs={'data-testid': 'topicText'})
        h2_title = span_tag.get_text(strip=True) if span_tag else h2_tag.get_text(strip=True)
    else:
        h2_title = ''

    # Xử lý các thẻ <section> con có 'data-testid' là 'topicGHead'
    child_sections = section.find_all('section')
    if child_sections:
        for child_section in child_sections:
            section_data.extend(extract_innermost_section(child_section, h2_title, json_title=json_title))
    else:
        # Xử lý nếu không có section con, chỉ có section cha
        section_data.extend(process_child_section(section, h2_title, json_title=json_title))

    # Xử lý các thẻ <p> với 'data-testid' là 'topicPara' ở bất kỳ đâu trong tài liệu
    section_data.extend(process_p_tags(section, h2_title, json_title=json_title))

    return section_data

def process_child_section(child_section, parent_title, json_title=None):
    """
    Xử lý một phần con (child section), xử lý các thẻ <h3> và <p> với các phương án thay thế thích hợp.
    """
    section_data = []
    h3_tags = child_section.find_all('h3')
    h3_titles = [h3.get_text(strip=True) for h3 in h3_tags]

    # Chỉ lấy nội dung <span> con của section này
    span_tags = child_section.find_all('span', attrs={'data-testid': 'topicText'})
    span_contents = [span.get_text(strip=True) for span in span_tags]

    li_tags = child_section.find_all('li', attrs={'data-testid': 'topicListItem'})
    li_contents = [li.get_text(strip=True) for li in li_tags]

    if h3_titles:
        for h3_title in h3_titles:
            title = f"{parent_title} - {h3_title}".strip() if parent_title else h3_title.strip()
            content = '\n'.join(span_contents + li_contents).strip()
            if title:
                section_data.append((title, content))
    
    return section_data

def process_p_tags(soup, parent_title, json_title=None):
    """
    Xử lý các thẻ <p> với 'data-testid' là 'topicPara' ở bất kỳ đâu trong tài liệu.
    """
    section_data = []
    p_tags = soup.find_all('p', attrs={'data-testid': 'topicPara'})

    for p_tag in p_tags:
        b_tag = p_tag.find('b', attrs={'data-testid': 'topicBold'})
        if b_tag and b_tag.find('span'):
            b_title = b_tag.find('span').get_text(strip=True)
            title = f"{parent_title} trên {b_title}".strip() if parent_title else b_title.strip()
            span_contents = [span.get_text(strip=True) for span in p_tag.find_all('span')]
            content = '\n'.join(span_contents).strip()
            if title:
                section_data.append((title, content))
    
    if not section_data and json_title:
        title = json_title.strip()
        content = '\n'.join(span_contents).strip()
        if title:
            section_data.append((title, content))

    return section_data

def scrape_page(url, json_title=None):
    """
    Lấy nội dung từ trang web dựa trên `url`, sử dụng `json_title` làm tiêu đề dự phòng.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        sections = soup.find_all('section', attrs={'data-testid': lambda x: x != 'footer'})
        section_data = []

        # Xử lý mỗi phần (section) cấp cao để trích xuất dữ liệu
        for section in sections:
            section_data.extend(extract_section_data(section, json_title=json_title))

        # Nếu không thu thập được dữ liệu từ các phần, thử cào nội dung từ các <div>
        if not section_data:
            divs = soup.find_all('div', attrs={'data-testid': 'topic-main-content'})
            for div in divs:
                # Dọn dẹp các <span> không cần thiết
                for span in div.find_all('span'):
                    if span.get_text().startswith('Tài liệu tham khảo'):
                        span.decompose()

                section_data.extend(process_p_tags(div, '', json_title=json_title))

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