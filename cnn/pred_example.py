import cnn
from PIL import Image

def main():
    # Фотография для анализа:
    path = 'pics/cat_man.jpg'
    img = Image.open(path)
    # Загружаем нейронную сеть:
    ml = cnn.load_cnn_model()
    # Делаем предикт фотографии:
    result = cnn.img_analyze(img, ml)
    print(result)

if __name__ == '__main__':
    main()
