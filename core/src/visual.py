from scipy.signal import savgol_filter
from matplotlib import pyplot as plt


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
