import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from gtts import gTTS

nltk.download('stopwords')

def scrape_news(company):
    search_url = f"https://www.bing.com/news/search?q={company}+news"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('div', class_='news-card')
    news_list = []
    for article in articles[:10]:
        title_tag = article.find('a', {'class': 'title'})
        title = title_tag.get_text(strip=True) if title_tag else "No Title"
        summary_tag = article.find('div', class_='snippet')
        summary = summary_tag.text.strip() if summary_tag else "No Summary"
        sentiment = analyze_sentiment(summary)
        topics = extract_topics(summary)
        news_list.append({"Title": title, "Summary": summary, "Sentiment": sentiment, "Topics": topics})
    return news_list

def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"

def extract_topics(text):
    words = text.lower().split()
    filtered_words = [word for word in words if word not in stopwords.words('english')]
    return list(set(filtered_words[:5]))

def generate_hindi_speech(text):
    tts = gTTS(text=text, lang='hi')
    file_path = "summary_audio.mp3"
    tts.save(file_path)
    return file_path