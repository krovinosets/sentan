import os
import re
import nltk
import psycopg2
from pymystem3 import Mystem
from dotenv import load_dotenv

from src.test import estimate_sentiment, make_plot, make_filtered_plot, make_ensemble_plot

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


if __name__ == "__main__":
    load_dotenv()
    comments: list[str] = get_all_comments_text(
        {
            'dbname': os.getenv("DATABASE_NAME"),
            'user': os.getenv("DATABASE_USER"),
            'password': os.getenv("DATABASE_PASSWORD"),
            'host': os.getenv("DATABASE_HOST"),
            'port': os.getenv("DATABASE_PORT")
        }
    )

    stop_words = nltk.corpus.stopwords.words('russian')

    texts: list[str] = []
    for i, comment in enumerate(comments):
        print("_________________________")
        cleared = clear_text(comment)
        print(f"{i}: cleared: {cleared}")

        texts.append(cleared)

        # cleaned = clean_stop_words(cleared, stop_words)
        # print(f"{i}: cleaned: {cleaned}")

        # lemma = lemmatize(cleaned)
        # print(f"{i}: lemmatize: {lemma}")

    sentiments = estimate_sentiment(texts)
    make_plot(sentiments)
    make_filtered_plot(sentiments)
    make_ensemble_plot(sentiments)
