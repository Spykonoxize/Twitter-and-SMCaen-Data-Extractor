import os
import re
import json
import tempfile
import pandas as pd
import emoji

def extract_twitter_features(input_file, selected_features, output_format='xlsx'):
    """
    Extract selected features from a tweets file.
    
    Args:
        input_file (str): Path to input file (CSV/JSON/XLSX/JS)
        selected_features (list): List of features to extract
        output_format (str): Output format ('xlsx' or 'csv')
    
    Returns:
        str: Path to output file
    """
    
    # Read input file
    file_ext = input_file.rsplit('.', 1)[1].lower()
    
    if file_ext == 'csv':
        df = pd.read_csv(input_file)
    elif file_ext == 'json':
        df = pd.read_json(input_file)
    elif file_ext in ['xlsx', 'xls']:
        df = pd.read_excel(input_file)
    elif file_ext == 'js':
        df = _parse_js_file(input_file)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")
    
    # Dictionary of transformations for each feature
    transformations = {
        'content': lambda x: _extract_content(df),
        'date': lambda x: _extract_date(df),
        'hashtags': lambda x: _extract_hashtags(df),
        'mentions': lambda x: _extract_mentions(df),
        'favorite_count': lambda x: _extract_favorite_count(df),
        'retweet_count': lambda x: _extract_retweet_count(df),
        'has_media': lambda x: _extract_has_media(df),
        'mention_count': lambda x: _extract_mention_count(df),
        'emojis': lambda x: _extract_emojis(df),
    }
    
    # Create output DataFrame with selected features
    output_df = pd.DataFrame()
    
    for feature in selected_features:
        if feature in transformations:
            output_df[feature] = transformations[feature](df)
    
    # Generate output file
    output_dir = tempfile.gettempdir()
    output_filename = f'tweets_extracted.{output_format}'
    output_path = os.path.join(output_dir, output_filename)
    
    if output_format == 'xlsx':
        output_df.to_excel(output_path, index=False, engine='openpyxl')
    elif output_format == 'csv':
        output_df.to_csv(output_path, index=False)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")
    
    return output_path

def _extract_content(df):
    """Extract tweet content"""
    possible_columns = ['full_text', 'text', 'content', 'tweet', 'message', 'body']
    for col in possible_columns:
        if col in df.columns:
            return df[col].fillna('').astype(str)
    return df.iloc[:, 0].fillna('').astype(str)

def _extract_date(df):
    """Extract tweet date in ISO format"""
    possible_columns = ['created_at', 'date', 'timestamp', 'time']
    
    for col in possible_columns:
        if col in df.columns:
            try:
                # Twitter format: "Sat Oct 01 18:01:20 +0000 2016"
                dates = pd.to_datetime(df[col], format='%a %b %d %H:%M:%S %z %Y', errors='coerce')
                if dates.notna().any():
                    return dates.dt.strftime('%Y-%m-%d %H:%M:%S').fillna('')
            except Exception:
                pass
            
            try:
                dates = pd.to_datetime(df[col], errors='coerce')
                return dates.dt.strftime('%Y-%m-%d %H:%M:%S').fillna('')
            except Exception:
                pass
    
    return pd.Series([''] * len(df))

def _extract_hashtags(df):
    """Extract hashtags from tweets"""
    # Try extracting from nested entities first
    if 'entities' in df.columns:
        hashtags = df['entities'].apply(lambda x: _extract_hashtags_from_entities(x))
        if hashtags.str.len().sum() > 0:
            return hashtags
    
    # Fallback to text extraction
    content_col = None
    possible_columns = ['full_text', 'text', 'content', 'tweet', 'message', 'body']
    
    for col in possible_columns:
        if col in df.columns:
            content_col = col
            break
    
    if content_col is None:
        content_col = df.columns[0]
    
    return df[content_col].fillna('').astype(str).apply(lambda x: _find_hashtags(str(x)))

def _extract_mentions(df):
    """Extract mentioned users"""
    # Try extracting from nested entities first
    if 'entities' in df.columns:
        mentions = df['entities'].apply(lambda x: _extract_mentions_from_entities(x))
        if mentions.str.len().sum() > 0:
            return mentions
    
    # Fallback to text extraction
    content_col = None
    possible_columns = ['full_text', 'text', 'content', 'tweet', 'message', 'body']
    
    for col in possible_columns:
        if col in df.columns:
            content_col = col
            break
    
    if content_col is None:
        content_col = df.columns[0]
    
    return df[content_col].fillna('').astype(str).apply(lambda x: _find_mentions(str(x)))

def _extract_favorite_count(df):
    """Extract favorite count"""
    possible_columns = ['favorite_count', 'likes', 'fav_count', 'favorites']
    for col in possible_columns:
        if col in df.columns:
            return pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    return pd.Series([0] * len(df))

def _extract_retweet_count(df):
    """Extract retweet count"""
    possible_columns = ['retweet_count', 'retweets', 'rt_count']
    for col in possible_columns:
        if col in df.columns:
            return pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    return pd.Series([0] * len(df))

def _extract_has_media(df):
    """Detect media presence"""
    # Check from entities
    if 'entities' in df.columns:
        has_media = df['entities'].apply(lambda x: _has_media_in_entities(x))
        if has_media.any():
            return has_media
    
    # Fallback to specific columns
    possible_columns = ['media', 'has_media', 'media_url', 'image_url', 'video_url']
    
    for col in possible_columns:
        if col in df.columns:
            return df[col].notna().astype(bool)
    
    return pd.Series([False] * len(df))

def _extract_mention_count(df):
    """Count mentioned users"""
    # Try extracting from nested entities first
    if 'entities' in df.columns:
        mention_count = df['entities'].apply(lambda x: _count_mentions_from_entities(x))
        if mention_count.sum() > 0:
            return mention_count
    
    # Fallback to text extraction
    content_col = None
    possible_columns = ['full_text', 'text', 'content', 'tweet', 'message', 'body']
    
    for col in possible_columns:
        if col in df.columns:
            content_col = col
            break
    
    if content_col is None:
        content_col = df.columns[0]
    
    return df[content_col].fillna('').astype(str).apply(lambda x: len(_find_mentions(str(x)).split(',')) if _find_mentions(str(x)).strip() else 0)

def _extract_emojis(df):
    """Extract emojis"""
    content_col = None
    possible_columns = ['full_text', 'text', 'content', 'tweet', 'message', 'body']
    
    for col in possible_columns:
        if col in df.columns:
            content_col = col
            break
    
    if content_col is None:
        content_col = df.columns[0]
    
    return df[content_col].fillna('').astype(str).apply(lambda x: _find_emojis(str(x)))

def _extract_hashtags_from_entities(entities):
    """Extract hashtags from nested JSON entity structure"""
    if not isinstance(entities, dict):
        return ''
    
    hashtags = entities.get('hashtags', [])
    if not hashtags:
        return ''
    
    if isinstance(hashtags, list):
        tags = [h.get('text', '') for h in hashtags if isinstance(h, dict) and h.get('text')]
        return ', '.join(tags) if tags else ''
    return ''

def _extract_mentions_from_entities(entities):
    """Extract mentions from nested JSON entity structure"""
    if not isinstance(entities, dict):
        return ''
    
    mentions = entities.get('user_mentions', [])
    if not mentions:
        return ''
    
    if isinstance(mentions, list):
        names = [m.get('screen_name', '') for m in mentions if isinstance(m, dict) and m.get('screen_name')]
        return ', '.join(names) if names else ''
    return ''

def _count_mentions_from_entities(entities):
    """Count mentions from nested JSON entity structure"""
    if not isinstance(entities, dict):
        return 0
    
    mentions = entities.get('user_mentions', [])
    if not mentions or not isinstance(mentions, list):
        return 0
    
    return len([m for m in mentions if isinstance(m, dict)])

def _has_media_in_entities(entities):
    """Detect media presence in entities"""
    if not isinstance(entities, dict):
        return False
    
    media = entities.get('media', [])
    return len(media) > 0 if isinstance(media, list) else False

def _find_hashtags(text):
    """Find all hashtags in text"""
    hashtags = re.findall(r'#\w+', text)
    return ', '.join(hashtags) if hashtags else ''

def _find_mentions(text):
    """Find all mentioned users in text"""
    mentions = re.findall(r'@\w+', text)
    return ', '.join(mentions) if mentions else ''

def _find_emojis(text):
    """Find all emojis in text"""
    emojis_found = [c for c in text if c in emoji.EMOJI_DATA]
    return ', '.join(emojis_found) if emojis_found else ''

def _parse_js_file(file_path):
    """
    Parse a Twitter JS file (format: window.YTD.tweets.part1 = [...])
    and return a pandas DataFrame.
    
    Args:
        file_path (str): Path to JS file
    
    Returns:
        pd.DataFrame: DataFrame containing tweet data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract JSON from JavaScript structure
    # Format: window.YTD.tweets.part1 = [...]
    match = re.search(r'window\.YTD\.tweets\.part\d+ = (\[.*\])', content, re.DOTALL)
    
    if not match:
        raise ValueError("Invalid JS file format. Expected: window.YTD.tweets.partX = [...]")
    
    json_str = match.group(1)
    
    # Parse JSON
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON: {str(e)}")
    
    # Extract tweets from nested structure
    tweets = []
    for item in data:
        if 'tweet' in item:
            tweets.append(item['tweet'])
        else:
            tweets.append(item)
    
    # Convert to DataFrame
    df = pd.json_normalize(tweets)
    return df
