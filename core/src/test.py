import re

import nltk
from scipy.signal import savgol_filter
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from matplotlib import pyplot as plt

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


texts = [
    "Это просто прекрасно, обожаю этот продукт!",
    "Ужасное обслуживание, никогда больше не вернусь.",
    "непримечательный сервис, нет хорошего.",
    "Прекрасный вид на горы",
    "А вы что хотите, что бы они в ваших интернетах сидели?",
    "Они там в Дум первый играть будут)",
    "Не задефузил бомбу - семья поехала дефузить рудники.",
    "это прямо л о л"
]


# sentences = []
# for text in texts:
#     sentences.append(clear_text(text))
#
#
# sentiments = estimate_sentiment(sentences)
# print(sentiments)

def make_plot(sentiments: list):
    plt.plot(sentiments)
    plt.xlabel('Номер предложения')
    plt.ylabel('Тональность')
    plt.show()


def make_filtered_plot(sentiments: list):
    filtered_sentiments = savgol_filter(sentiments, window_length=len(sentiments) // 15, polyorder=0)
    plt.plot(filtered_sentiments)
    plt.xlabel('Номер предложения')
    plt.ylabel('Тональность')
    plt.show()


def ensemble_filter(data: list, n_filters=100, polyorder=0, **savgol_args) -> list:
    """
    Применяет ансамблевый фильтр к входным данным

    Parameters:
    data (list): входной массив данных
    n_filters (int, optional): число фильтров участвующих в сглаживании
    """
    filt = 0
    start = len(data)//10
    stop = len(data)//4
    step = (stop-start)//n_filters
    if step == 0:
        step = 1
    # Варьируем размер окна и усредняем результат
    for window_size in range(start, stop, step):
        res = savgol_filter(data, window_length=window_size, polyorder=polyorder, **savgol_args)
        filt += res
    return filt/n_filters


def make_ensemble_plot(sentiments: list):
    filtered_sentiments = ensemble_filter(sentiments, polyorder=0)
    plt.plot(filtered_sentiments)
    plt.xlabel('Номер предложения')
    plt.ylabel('Тональность')
    plt.show()
