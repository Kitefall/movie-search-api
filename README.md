# Movie Search API

Сервис для семантического поиска фильмов по их описанию. Полнофункциональное веб-приложение с бэкендом на FastAPI, ML-моделью на scikit-learn (TF-IDF + KNN), асинхронной обработкой через RabbitMQ, базой данных PostgreSQL, интерфейсом на Gradio и прокси-сервером Nginx. Реализована аутентификация, ролевая модель, система внутренней валюты для платного доступа к ML-функциям.

> **Примечание:** Проект изначально разрабатывался с использованием GitLab (CI/CD, репозиторий). В данный момент код размещён на GitHub для публичного портфолио.

## Возможности

- Регистрация и аутентификация пользователей (JWT)
- Роли: обычный пользователь и администратор
- Семантический поиск фильмов по текстовому описанию
- Внутренняя валюта (койны) для оплаты запросов к ML-модели
- История всех предсказаний пользователя
- Административные функции: управление пользователями, пополнение балансов, просмотр статистики
- Интерактивный пользовательский интерфейс на Gradio
- Полная контейнеризация с помощью Docker Compose
- Набор тестов pytest

## Архитектура

Проект состоит из нескольких микросервисов, взаимодействующих между собой:

- **FastAPI** – основной REST API сервер (порт 80 через Nginx).
- **PostgreSQL** – реляционная база данных для хранения пользователей, фильмов, транзакций и истории предсказаний.
- **RabbitMQ** – брокер сообщений для асинхронной обработки ML-запросов.
- **ML Worker** – отдельный контейнер, который загружает обученную модель (TF-IDF + KNN) и обрабатывает задания из очереди RabbitMQ.
- **Nginx** – reverse proxy, маршрутизирующий запросы на FastAPI и Gradio.
- **Gradio** – лёгкий веб-интерфейс для демонстрации поиска фильмов.

Все компоненты связаны через `docker-compose.yaml` и запускаются одной командой.

## Структура проекта

```
movie-search-api/
├── app/ # Основной код приложения FastAPI
│ ├── api.py # Точка входа приложения
│ ├── config.py # Конфигурация приложения
│ ├── database/ # Работа с базой данных (SQLAlchemy)
│ │ ├── database.py
│ │ ├── database_config.py
│ │ └── crud/ # CRUD-операции для сущностей
│ ├── dependencies/ # Зависимости FastAPI
│ ├── models/ # Модели SQLAlchemy
│ ├── routes/ # Маршруты API
│ ├── schemas/ # Pydantic-схемы
│ ├── services/ # Бизнес-логика (сервисы)
│ └── tests/ # Тесты pytest
├── ml_workers/ # Сервис ML-воркера
│ ├── worker.py # Логика обработки сообщений RabbitMQ
│ ├── knn_model.joblib # Обученная модель KNN
│ ├── tfidf_vectorizer.joblib # Векторизатор TF-IDF
│ └── ...
├── nginx/ # Конфигурация Nginx
├── docker-compose.yaml # Оркестрация всех сервисов
├── .env.example # Пример переменных окружения
└── README.md
```

## Установка и запуск

### Предварительные требования

- Установленный Docker и Docker Compose
- Git

### Шаги

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/Kitefall/movie-search-api.git
   cd movie-search-api
   ```
2. **Настройте переменные окружения:**

    - Скопируйте файл .env.example в .env:

        `cp .env.example .env`

    - Отредактируйте .env, указав секретные ключи, доступы к базе данных, RabbitMQ и другие параметры (примеры внутри файла).

### Получение датасета

Из-за ограничений GitHub на размер файлов, датасет `my_data.csv` не хранится в репозитории. Скачайте его по ссылке:

[Скачать my_data.csv](https://drive.google.com/file/d/1H5xjFl8qMtaltloLxyxBZyXqZjKpCw5E/view?usp=sharing)

Поместите файл в папку `app/database/` перед запуском приложения.

3. **Запустите приложение:**

```bash
docker-compose up --build
```

4. **Доступ к сервисам:**

- Основной API: [http://localhost/](http://localhost/)
- Swagger UI: [http://localhost/docs](http://localhost/docs)
- Gradio интерфейс: [http://localhost/gradio](http://localhost/gradio) (если маршрут настроен в Nginx)

## Тестирование

Запуск тестов (из корня проекта, внутри контейнера или локально):

```bash
pytest
```

Тесты покрывают аутентификацию, пользовательские сценарии, работу с моделью и административные функции.

## Технологии

- Backend: FastAPI, Uvicorn, Starlette, Pydantic, SQLAlchemy, FastAPI Users, AuthX

- База данных: PostgreSQL (psycopg2-binary, asyncpg)

- ML: scikit-learn (TF-IDF, KNN), NumPy, Pandas, Joblib

- Очередь сообщений: RabbitMQ, FastStream

- UI: Gradio

- Инфраструктура: Docker, Docker Compose, Nginx

- Безопасность: Passlib, Email Validator

- Тестирование: pytest

## Демонстрация

Видео с разбором проекта и демонстрацией работы: Ссылка на [Rutube](https://rutube.ru/video/private/eb5d9249d122dcfcc6717b0da370386d/?p=z8aX-3pzJF9JZzPlnR3fBA)