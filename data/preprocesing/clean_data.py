from nltk.tokenize import word_tokenize, sent_tokenize
import pandas as pd
import re
import string
from pyvi import ViTokenizer
import nltk
from transformers import AutoTokenizer

# Tải các tài nguyên cần thiết từ NLTK
nltk.download('punkt')

# Load the tokenizer (e.g., BARTpho or any other tokenizer you are using)
tokenizer = AutoTokenizer.from_pretrained('vinai/bartpho-syllable')

def clean_document(doc):
    """Clean a document by tokenizing, lowercasing, removing punctuation, and splitting into words."""
    # Tokenize the document using ViTokenizer
    doc = ViTokenizer.tokenize(doc)
    
    # Convert the document to lowercase
    doc = doc.lower()

    # Remove punctuation (except underscores) and emoji icons
    doc = remove_punctuation(doc)
    
    # Split the document into words (tokens)
    tokens = doc.split()

    # Filter out any empty tokens
    tokens = [word for word in tokens if word]
    
    return " ".join(tokens)

def remove_punctuation(text):
    """Remove punctuation, redundant spaces, and emoji icons from the text."""
    # Create a translation table to remove punctuation except underscores
    translator = str.maketrans('', '', string.punctuation.replace("_", ""))
    
    # Remove punctuation
    text = text.translate(translator)
    
    # Remove redundant spaces and line breaks
    text = re.sub('[\n ]+', ' ', text).strip()

    # Remove emoji icons
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
    
    text = re.sub(emoji_pattern, '', text)
    
    return text

def split_text_by_length(text, max_length=1024):
    """Tách văn bản thành các phần nhỏ hơn hoặc bằng max_length tokens."""
    # Tách văn bản thành các câu
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(tokenizer.encode(sentence, add_special_tokens=False))
        
        if sentence_length > max_length:
            # Nếu câu đơn lẻ dài hơn max_length, chia câu thành các phần nhỏ hơn
            while sentence_length > max_length:
                part = tokenizer.decode(tokenizer.encode(sentence, add_special_tokens=False)[:max_length], skip_special_tokens=True)
                chunks.append(part)
                sentence = sentence[len(tokenizer.decode(tokenizer.encode(part, add_special_tokens=False))):]
                sentence_length = len(tokenizer.encode(sentence, add_special_tokens=False))
            
            # Thêm phần còn lại của câu vào chunk hiện tại
            if sentence_length <= max_length:
                if current_length + sentence_length > max_length:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_length = 0
                current_chunk.append(sentence)
                current_length += sentence_length
        else:
            # Nếu câu nhỏ hơn max_length, thêm vào chunk hiện tại
            if current_length + sentence_length > max_length:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

    # Thêm phần còn lại của chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def transform_load(df):
    """Transform raw data to usable text, apply processing functions, and handle splitting."""
    # Fill NaN values with empty strings
    df = df.fillna('')
    
    # Initialize a new DataFrame to store the split data
    new_rows = []
    
    for _, row in df.iterrows():
        title = row['Title']
        content = row['Detailed Content']
        reference_link = row['Reference Link']  # Lấy thông tin liên kết
        
        # Split content based on max_length before cleaning
        content_chunks = split_text_by_length(content, max_length=1024)
        
        for chunk in content_chunks:
            cleaned_chunk = clean_document(chunk)  # Clean each chunk after splitting
            new_row = {
                'Title': clean_document(title),
                'Detailed Content': cleaned_chunk,
                'Reference Link': reference_link  # Giữ lại liên kết
            }
            new_rows.append(new_row)
    
    # Convert new_rows into a DataFrame
    new_df = pd.DataFrame(new_rows)
    
    return new_df


def save_to_csv(processed_news, output_path):
    """Save cleaned data to CSV."""
    processed_news.to_csv(output_path, index=False, encoding='utf-8')

# Example usage
if __name__ == "__main__":
    # Path to your input CSV file
    input_csv_path = '../csv/medical.csv'  # Change this to your actual CSV file path

    # Load the CSV file
    df = pd.read_csv(input_csv_path)

    # Transform and process the data
    processed_news = transform_load(df)

    # Path to save the processed CSV
    output_csv_path = '../csv/processed_medical.csv'
    
    # Save processed data to CSV
    save_to_csv(processed_news, output_csv_path)

    print(f"Processed data has been saved to {output_csv_path}.")
