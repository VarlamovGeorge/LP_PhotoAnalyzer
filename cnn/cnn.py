import tensorflow
from tensorflow.python.keras.models import model_from_json
from keras.preprocessing import image
import numpy as np

import trained.cnn_properties as cp

cp.classes_list.sort()
# cnn_ver = cp.ver
cnn_descr = cp.description
cnn_date = cp.create_date


def init():
    model = load_cnn_model()
    graph = tensorflow.get_default_graph()
    return model, graph


def load_cnn_model():
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
    x /= 255.
    x -= 0.5
    x *= 2.
    return x


def img_analyze(input_image, loaded_model):
    # Грузим картинку для распознавания
    img = input_image
    width_height_tuple = (300, 300)
    if img.size != width_height_tuple:
        img = img.resize(width_height_tuple)

    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)

    # Нормализуем изображение
    x = preprocess_input(x)

    # preds = loaded_model.predict(x)
    # print('Predicted:', preds)

    y_prob = loaded_model.predict(x)
    # y_classes = y_prob.argmax(axis=-1)
    # print(y_classes, y_prob)

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
        # prob = "%.5f" % round(prob,5)
        # print("I have %s%% sure that it belongs to %s." % (prob, predicted_label))

        # Добавляем в словарь только классы с весами больше 0
        if round(prob, 5) != 0:
            prediction['labels'][predicted_label] = round(prob, 5)

    return prediction
