import pandas as pd
import requests
from bs4 import BeautifulSoup

def scrape_section_content(url):
    """
    Cào nội dung từ các thẻ <section> trong trang web và trả về nội dung của các thẻ <span>.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Lấy tất cả các thẻ <section> trên trang
        sections = soup.find_all('section')

        # Lấy nội dung từ tất cả các thẻ <span> trong các thẻ <section>
        context_list = []
        for section in sections:
            spans = section.find_all('span')
            for span in spans:
                context_list.append(span.get_text(strip=True))
        
        # Kết hợp nội dung từ các thẻ <span> thành một chuỗi
        context = ' '.join(context_list)
        return context

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""

def update_csv_with_context(input_csv, output_csv):
    """
    Đọc file CSV đầu vào, cào nội dung từ các liên kết và cập nhật cột 'Context' trong file CSV đầu ra.
    """
    # Đọc dữ liệu từ file CSV
    df = pd.read_csv(input_csv)

    # Tạo một danh sách để lưu trữ dữ liệu đã cập nhật
    updated_rows = []

    for _, row in df.iterrows():
        reference_link = row.get('Reference Link')
        if reference_link:
            context = scrape_section_content(reference_link)
            updated_row = row.copy()
            updated_row['Context'] = context
            updated_rows.append(updated_row)
        else:
            updated_row = row.copy()
            updated_row['Context'] = ''
            updated_rows.append(updated_row)

    # Tạo DataFrame mới từ dữ liệu đã cập nhật
    updated_df = pd.DataFrame(updated_rows)

    # Lưu DataFrame mới vào file CSV đầu ra
    updated_df.to_csv(output_csv, index=False)

# Đặt tên file CSV đầu vào và đầu ra
input_csv = '../csv/processed_medical.csv'  # Đường dẫn đến file CSV đầu vào
output_csv = '../csv/medical_with_context.csv'  # Đường dẫn đến file CSV đầu ra

# Cập nhật file CSV với nội dung từ các liên kết
update_csv_with_context(input_csv, output_csv)
