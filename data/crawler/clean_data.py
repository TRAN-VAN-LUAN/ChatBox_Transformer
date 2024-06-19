import pandas as pd
import os
import re
import string
from tqdm import tqdm
from pyvi import ViTokenizer


def remove_punctuation(comment):
    # Create a translation table
    translator = str.maketrans('', '', string.punctuation)
    # Remove punctuation
    new_string = comment.translate(translator)
    # Remove redundant space and break sign
    new_string = re.sub('[\n ]+', ' ', new_string)
    # Remove emoji icon
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

def get_info(topic, processed_news):
    temp = processed_news[processed_news.topic == topic]
    return temp['article_id'].tolist(), temp['tag'].tolist()

def transform_load(df):
    """Transform the raw data to usable text and apply processing functions
    """
    # Select necessary columns and fill NaN values
    processed_news = df[['title', 'content', 'subtopic']].fillna('')
    
    # Apply punctuation removal and tokenization
    processed_news['content'] = processed_news['content'].apply(lambda x: x.lower())
    processed_news['content'] = processed_news['content'].apply(remove_punctuation)
    processed_news['content'] = processed_news['content'].apply(ViTokenizer.tokenize)
    # Apply punctuation removal and tokenization
    processed_news['title'] = processed_news['title'].apply(lambda x: x.lower())
    processed_news['title'] = processed_news['title'].apply(remove_punctuation)
    processed_news['title'] = processed_news['title'].apply(ViTokenizer.tokenize)

    return processed_news

def save_to_csv(processed_news):
    """Save cleaned data to CSV
    """
    processed_news.to_csv('data/csv/articles.csv', index=False)

# Example usage
if __name__ == "__main__":
    # Example DataFrame creation (replace with your actual DataFrame loading)
    df = pd.read_csv('data/csv/articles.csv')

    # Transform and process the data
    processed_news = transform_load(df)

    # Save processed data to CSV
    save_to_csv(processed_news)
