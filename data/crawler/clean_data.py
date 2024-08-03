import pandas as pd
import re
import string
from pyvi import ViTokenizer

def remove_punctuation(comment):
    # Tạo bảng dịch để loại bỏ dấu câu
    translator = str.maketrans('', '', string.punctuation)
    # Loại bỏ dấu câu
    new_string = comment.translate(translator)
    # Loại bỏ khoảng trắng và dấu xuống dòng thừa
    new_string = re.sub('[\n ]+', ' ', new_string)
    # Loại bỏ biểu tượng cảm xúc
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642"
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                            "]+", flags=re.UNICODE)
    new_string = re.sub(emoji_pattern, '', new_string)
    return new_string

def transform_load(df):
    """Transform the raw data to usable text and apply processing functions."""
    # Fill NaN values with empty strings
    df = df.fillna('')
    
    # Apply punctuation removal and tokenization to the content column
    df['Content'] = df['Content'].apply(lambda x: x.lower()) # Lowercase content
    df['Content'] = df['Content'].apply(remove_punctuation)  # Remove punctuation and special chars
    df['Content'] = df['Content'].apply(ViTokenizer.tokenize)  # Tokenize Vietnamese text

    # Apply punctuation removal and tokenization to the title column
    df['Title'] = df['Title'].apply(lambda x: x.lower()) # Lowercase title
    df['Title'] = df['Title'].apply(remove_punctuation)  # Remove punctuation and special chars
    df['Title'] = df['Title'].apply(ViTokenizer.tokenize)  # Tokenize Vietnamese text

    return df

def save_to_csv(processed_news, output_path):
    """Save cleaned data to CSV."""
    processed_news.to_csv(output_path, index=False, encoding='utf-8')

# Example usage
if __name__ == "__main__":
    # Path to your input CSV file
    input_csv_path = 'output2.csv'  # Change this to your actual CSV file path

    # Load the CSV file
    df = pd.read_csv(input_csv_path)

    # Transform and process the data
    processed_news = transform_load(df)

    # Path to save the processed CSV
    output_csv_path = 'processed_output.csv'
    
    # Save processed data to CSV
    save_to_csv(processed_news, output_csv_path)

    print(f"Processed data has been saved to {output_csv_path}.")

