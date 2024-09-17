import pandas as pd

def load_stopwords(file_path: str) -> list:
    """
    Đọc danh sách stopwords từ một file.

    Args:
        file_path (str): Đường dẫn tới file chứa stopwords.

    Returns:
        list: Danh sách các stopwords.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            stopwords = [line.strip() for line in file if line.strip()]
        return stopwords
    except FileNotFoundError:
        print(f"Không tìm thấy file: {file_path}")
        return []
    except Exception as e:
        print(f"Đã xảy ra lỗi khi đọc file: {e}")
        return []


def remove_stopwords(text: str, stopwords: list) -> str:
    """
    Loại bỏ stopwords khỏi văn bản.

    Args:
        text (str): Văn bản cần xử lý.
        stopwords (list): Danh sách các stopwords.

    Returns:
        str: Văn bản sau khi loại bỏ stopwords.
    """
    stopwords_set = set(stopwords)
    filtered_words = [word for word in text.split() if word.lower() not in stopwords_set]
    cleaned_text = ' '.join(filtered_words)

    return cleaned_text


def main():
    # Đường dẫn tới file chứa danh sách stopwords
    stopword_file_path = '../vietnamese-stopwords-dash.txt'  

    # Tải danh sách stopwords từ file
    stopwords = load_stopwords(stopword_file_path)
    if not stopwords:
        print("Danh sách stopwords trống hoặc không thể tải.")
        return
    
    input_csv_path = '../csv/processed_medical.csv'  # Cập nhật đường dẫn tới file CSV của bạn

    # Load the CSV file
    df = pd.read_csv(input_csv_path)

    df['Title'] = df['Title'].apply(lambda x: remove_stopwords(x, stopwords))
    df['Detailed Content'] = df['Detailed Content'].apply(lambda x: remove_stopwords(x, stopwords))

    # In kết quả
    print("DataFrame đã được làm sạch:")
    print(df)
    output_csv_path = '../csv/processed_medical.csv'  # Đường dẫn để lưu file CSV đã làm sạch
    df.to_csv(output_csv_path, index=False)


if __name__ == '__main__':
    main()
