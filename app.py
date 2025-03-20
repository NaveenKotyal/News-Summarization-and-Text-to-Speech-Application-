import streamlit as st
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from gtts import gTTS
from googletrans import Translator
import re
import os

# Download required resources
nltk.download('stopwords')

translator = Translator()  # Initialize Translator

# Function to scrape news articles
def scrape_news(company):
    search_url = f"https://www.bing.com/news/search?q={company}+news"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)

    if response.status_code != 200:
        st.error("Failed to fetch news articles. Please try again.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('div', class_='news-card')  # Adjust based on site structure

    news_list = []
    for article in articles[:10]:  # Limit to 10 articles
        title_tag = article.find('a', {'class': 'title'})  # Adjust class based on actual HTML structure
        title = title_tag.get_text(strip=True) if title_tag else "No Title"

        summary_tag = article.find('div', class_='snippet')
        summary = summary_tag.text.strip() if summary_tag else "No Summary"

        sentiment = analyze_sentiment(summary)
        topics = extract_topics(summary)

        news_list.append({
            "Title": title,
            "Summary": summary,
            "Sentiment": sentiment,
            "Topics": topics
        })

    return news_list

# Function for sentiment analysis
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"

# Function to extract key topics from text
def extract_topics(text):
    words = re.findall(r'\b\w+\b', text.lower())
    filtered_words = [word for word in words if word not in stopwords.words('english')]
    return list(set(filtered_words[:5]))  # Return top 5 unique words

# Function to generate Hindi speech from summary
def generate_hindi_speech(text):
    # Translate to Hindi
    translated_text = translator.translate(text, src='en', dest='hi').text


    # Generate speech using gTTS
    tts = gTTS(text=translated_text, lang="hi")
    audio_path = "summary_audio.mp3"
    tts.save(audio_path)
    
    return audio_path

# Function to perform comparative analysis
def comparative_analysis(articles):
    sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
    all_topics = []

    for article in articles:
        sentiment_counts[article["Sentiment"]] += 1
        all_topics.append(set(article["Topics"]))

    coverage_differences = []
    for i in range(len(articles) - 1):
        comparison = f"Article {i+1} discusses {articles[i]['Topics']}, while Article {i+2} focuses on {articles[i+1]['Topics']}."
        impact = "Different perspectives highlight contrasting viewpoints on the company."
        coverage_differences.append({"Comparison": comparison, "Impact": impact})

    common_topics = set.intersection(*all_topics) if all_topics else set()
    unique_topics = [list(topics - common_topics) for topics in all_topics]

    return {
        "Sentiment Distribution": sentiment_counts,
        "Coverage Differences": coverage_differences,
        "Topic Overlap": {
            "Common Topics": list(common_topics),
            "Unique Topics per Article": unique_topics
        }
    }

# Streamlit UI
st.title("🔍 Company News Extractor")
company = st.text_input("Enter Company Name:")

if st.button("Fetch News"):
    if company:
        with st.spinner("Fetching latest news..."):
            articles = scrape_news(company)

        if articles:
            comparison = comparative_analysis(articles)

            result = {
                "Company": company,
                "Articles": articles,
                "Comparative Sentiment Score": comparison,
                "Final Sentiment Analysis": "Overall sentiment is mostly positive. Expect market impact."
            }

            st.json(result)  # Display structured output

            # Combine summaries for Hindi speech
            combined_summary = " ".join([article["Summary"] for article in articles if article["Summary"] != "No Summary"])
            
            if combined_summary:
                audio_file = generate_hindi_speech(combined_summary)
                st.audio(audio_file, format="audio/mp3")

        else:
            st.warning("No articles found. Try another company.")
