import tensorflow
from tensorflow.python.keras.utils import np_utils
from tensorflow.python.keras.models import model_from_json
from keras.preprocessing import image
from keras.applications.imagenet_utils import decode_predictions
import os
import numpy as np

import trained.cnn_properties as cp

cp.classes_list.sort()
cnn_descr = cp.description
cnn_date = cp.create_date


def init():
    '''
    Инициализирующая функция, передающая внешней программе глобальные переменные model и graph.
    '''
    
    model = load_cnn_model()
    graph = tensorflow.get_default_graph()
    return model, graph


def load_cnn_model():
    '''
    Функция загрузки модели нейронной сети из json-файла с архитектурой сети, и HDF5-файла с данными о весах.
    Указанные файлы с параметрами модели должны быть расположены в ./trained/cnn.json и ./trained/cnn.h5.
    '''

    # Загружаем нейронную сеть, созданную с помощью Keras:
    # Загружаем данные об архитектуре сети из файла json
    json_file = open('trained/cnn.json', "r")
    loaded_model_json = json_file.read()
    json_file.close()
    # Создаем модель на основе загруженных данных
    loaded_model = model_from_json(loaded_model_json)
    # Загружаем веса в модель
    loaded_model.load_weights('trained/cnn.h5')

    # Компилируем модель
    loaded_model.compile(loss='categorical_crossentropy',
                  optimizer='rmsprop',
                  metrics=['categorical_accuracy'])

    return loaded_model

def preprocess_input(x):
    '''
    Нормализация изображения x, поданного в виде 4D numpy массива.
    '''
    x /= 255.
    x -= 0.5
    x *= 2.
    return x

def img_analyze(input_image, loaded_model):
    '''
    Функция разпознавания объектов на фотографии. Результатом является словарь с информацией об
    используемой модели сверточной нейронной сети и дате ее создания. А также перечень классов,
    к которым модель относит обрабатываемое изображение с весами больше 1e-5.
    Использование: img_analyze(input_image, loaded_model)
    - input_image - анализируемое jpg-изображение в формате pillow-объекта;
    - loaded_model - загруженная из .h5 и .json файлов модель нейронной сети (см. функцию load_cnn_model()).
    Результат:
    {
    'cnn_info': {
        'alg_name': cnn_descr, 
        'create_date': cnn_date},
    'labels': {},
    }
    - cnn_descr - краткое описание модели в формате str;
    - cnn_date - дата создания модели в формате 'YYYY-MM-DD HH:MI:SS'.
    '''

    # Грузим картинку для распознавания
    img = input_image
    width_height_tuple = (300, 300)
    if img.size != width_height_tuple:
        img = img.resize(width_height_tuple)
    
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)

    # Нормализуем изображение
    x = preprocess_input(x)

    y_prob = loaded_model.predict(x) 
    y_classes = y_prob.argmax(axis=-1)

    # Сортируем вероятности классов в убывающем порядке
    sorting = (-y_prob).argsort()

    # Преобразуем в обычный массив
    cls_sorted = sorting[0]

    # Словарь с результатами
    prediction = {
            'cnn_info': {
                'alg_name': cnn_descr, 
                'create_date': cnn_date},
            'labels': {},
            }
    for value in cls_sorted:
        predicted_label = cp.classes_list[value]
        prob = y_prob[0][value]
        
        # Добавляем в словарь только классы с весами больше 0
        if round(prob,5) != 0:
            prediction['labels'][predicted_label] = round(prob,5)

    return prediction
