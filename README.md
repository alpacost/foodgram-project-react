## Описание
Проект Foodgram предназначен для хранения рецептов и соответствующих им фотографий. Он позволяет пользователям сохранять рецепты, добавлять фотографии и описания, а также генерировать списки покупок необходимых ингредиентов.

## Запуск на локальной машине
**Переход в папку с docker-compose**

    cd infra/
**Создать .env**

    touch .env
**Шаблон заполнения .env**
~~~
DB_ENGINE= указываем название базы данных
DB_NAME= имя базы данных
POSTGRES_USER= логин для подключения к базе данных
POSTGRES_PASSWORD= пароль для подключения к БД
DB_HOST= название сервиса (контейнера)
DB_PORT= порт для подключения к БД
~~~

**Собрать и запустить проект**

    docker-compose up -d --build

**Провести миграции**

    docker-compose  infra-backend python manage.py migrate    
**Создать суперпользователя**

    docker-compose exec infra-backend python manage.py createsuperuser 
    
**Собрать статику**

    docker-compose exec infra-backendb python manage.py collectstatic --no-input 
    
**Доступ к админке**

    http://localhost/admin/ 
