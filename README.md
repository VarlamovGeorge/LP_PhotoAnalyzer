# LP_PhotoAnalyzer
Анализатор фотографий домашнего фото-архива "Photo Analyzer"

## Цель проекта
Разработка системы поиска контента в домашнем цифровом фотоархиве на основании содержимого изображений.

## Функциональность
1. Анализ и индексация всех фотографий из заданного каталога и всех его вложенных каталогов по следующим параметрам:
- дата и время съёмки;
- (TODO) место съемки;
- наличие на фотографии каких-либо шаблонных предметов/окружения (машина, лето, море, дети, коты, собаки, документы и т.д.).
2. Возможность поиска изображений по критериям из п.1.

    *Пример:* показать все фото, сделанные за июль 2009 года, где есть люди и море.

3. Автоматическая обработка добавленных в архив (или каталог) фотографий с настройками запуска алгоритма (к примеру производить анализ новых фотографий только ночью с 2:00 до 8:00 или каждые N минут).
4. (TODO) Возможность добавления к папке и фотографиям пользовательских тегов для последующего поиска.
5. (TODO) Отображение групп фотографий на карте мира на основании метаданных о месте съёмки.
6. (TODO) Возможность находить на фотографиях конкретных людей (например: себя, маму, жену, друга).
7. (TODO) Создание видео (набор слайдов) или публикации в соцсети псевдослучайных фотографий на какую-то тему.

## Документация:
1. [Сверточная нейронная сеть](https://github.com/VarlamovGeorge/LP_PhotoAnalyzer/blob/master/docs/cnn/README.md)
2. [Текстовое описание БД и веб-приложения](https://github.com/VarlamovGeorge/LP_PhotoAnalyzer/tree/master/docs/webapp/README.md)
3. [Архитектура](https://raw.githubusercontent.com/VarlamovGeorge/LP_PhotoAnalyzer/master/docs/architecture.png)
4. [Структура БД](https://raw.githubusercontent.com/VarlamovGeorge/LP_PhotoAnalyzer/master/docs/db_descr/db.jpg)
5. [Реализация](https://github.com/VarlamovGeorge/LP_PhotoAnalyzer/blob/master/docs/implementation.png)

# Настройка системы (wiki):
1. [Действия пользователя перед запуском](https://github.com/VarlamovGeorge/LP_PhotoAnalyzer/wiki/First_Start)
2. [Управляем Docker-compose](https://github.com/VarlamovGeorge/LP_PhotoAnalyzer/wiki/Docker_compose)
3. [Работа с БД на Postgres](https://github.com/VarlamovGeorge/LP_PhotoAnalyzer/wiki/Postgres)
