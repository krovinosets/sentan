import re
import nltk
import psycopg2
from pymystem3 import Mystem
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

nltk.download('stopwords')


def get_all_comments_text(db_params: dict) -> list[str]:
    connection = psycopg2.connect(**db_params)
    with connection.cursor() as cursor:
        cursor.execute("SELECT text FROM vk_comments")
        texts = [row[0] for row in cursor.fetchall()]
    connection.close()

    return texts


def clear_text(text: str) -> str:
    """
    Функция получает на вход строчку текста

    Удаляет с помощью регулярного выражения
    все не кириллические символы и приводит
    слова к нижнему регистру

    Возвращает обработанную строчку
    """

    cleared_text = re.sub(r'[^А-яЁё]+', ' ', text).lower()
    return ' '.join(cleared_text.split())


def clean_stop_words(text: str, stopwords: list):
    """
    Функция получает:
    * text -- строчку текста
    * stopwords -- список стоп слов для исключения
    из текста

    Возвращает строчку текста с исключенными стоп словами
    """

    text = [word for word in text.split() if word not in stopwords]
    return " ".join(text)


def lemmatize(text: str):
    return Mystem().lemmatize(text)


model_checkpoint = 'cointegrated/rubert-tiny-sentiment-balanced'
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
model = AutoModelForSequenceClassification.from_pretrained(model_checkpoint)
if torch.cuda.is_available():
    model.cuda()


def estimate_sentiment(messages: list) -> list:
    sentiment_out = []
    for text in messages:
        with torch.no_grad():
            inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True).to(model.device)
            proba = torch.sigmoid(model(**inputs).logits).cpu().numpy()[0]
            sentiment_out.append(proba.dot([-1, 0, 1]))
    return sentiment_out
