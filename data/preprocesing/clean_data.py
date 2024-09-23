from nltk.tokenize import sent_tokenize
import pandas as pd
import re
import string
from pyvi import ViTokenizer
import nltk
from transformers import AutoTokenizer

# Download necessary NLTK resources
nltk.download('punkt')

# Load the tokenizer (e.g., BARTpho or any other tokenizer you are using)
tokenizer = AutoTokenizer.from_pretrained('vinai/bartpho-syllable')

def clean_text(text, keep_period=False):
    """Clean text by tokenizing, lowercasing, removing punctuation, and emojis."""
    # Tokenize and lowercase
    text = ViTokenizer.tokenize(text).lower()
    
    # Remove punctuation and emojis
    text = remove_punctuation(text, keep_period)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def remove_punctuation(text, keep_period=False):
    """Remove punctuation, emojis, and optionally keep periods."""
    # Define punctuation to remove
    if keep_period:
        punctuation_to_remove = string.punctuation.replace(".", "").replace("_", "")
    else:
        punctuation_to_remove = string.punctuation.replace("_", "")

    # Create translation table
    translator = str.maketrans('', '', punctuation_to_remove)
    text = text.translate(translator)

    # Remove emojis
    emoji_pattern = re.compile(
        "[" 
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
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
    text = emoji_pattern.sub('', text)
    
    return text

def split_text_by_length(text, max_length=150):
    """Split text into chunks with a maximum number of tokens."""
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(tokenizer.encode(sentence, add_special_tokens=False))
        
        if sentence_length > max_length:
            # Split long sentences
            while sentence_length > max_length:
                part = tokenizer.decode(tokenizer.encode(sentence, add_special_tokens=False)[:max_length], skip_special_tokens=True)
                chunks.append(part)
                sentence = sentence[len(tokenizer.decode(tokenizer.encode(part, add_special_tokens=False))):]
                sentence_length = len(tokenizer.encode(sentence, add_special_tokens=False))
            
            # Add the remaining part of the sentence
            if sentence_length <= max_length:
                if current_length + sentence_length > max_length:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_length = 0
                current_chunk.append(sentence)
                current_length += sentence_length
        else:
            if current_length + sentence_length > max_length:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

    # Add remaining chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def transform_load(df):
    """Transform raw data to usable text, apply processing functions, and handle splitting."""
    # Fill NaN values with empty strings
    df = df.fillna('')
    
    new_rows = []
    
    for _, row in df.iterrows():
        title = row['Title']
        content = row['Detailed Content']
        reference_link = row['Reference Link']
        context = row['Context']
        
        # Split and clean content
        content_chunks = split_text_by_length(content, max_length=1024)
        
        for chunk in content_chunks:
            cleaned_chunk = clean_text(chunk)
            new_row = {
                'Title': clean_text(title),
                'Detailed Content': cleaned_chunk,
                'Reference Link': reference_link,
                'Context': clean_text(context, keep_period=True)
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
    input_csv_path = '../csv/medical_with_context.csv'
    output_csv_path = '../csv/processed_medical_cleaned.csv'
    
    # Load the CSV file
    df = pd.read_csv(input_csv_path)
    
    # Transform and process the data
    processed_news = transform_load(df)
    
    # Save processed data to CSV
    save_to_csv(processed_news, output_csv_path)

    print(f"Processed data has been saved to {output_csv_path}.")
