## Дипломный проект в рамках программы python web-developer от <span style="color:red">Y</span><span style="color:yellow">andex-Praktikum</span>

![example workflow](https://github.com/kurtKostein/foodgram-project-react/actions/workflows/main.yaml/badge.svg)

#### [пример работающего проекта](http://62.84.121.130/recipes)

Администратор сайта:

- логин: `foodgram@foodgram.com`
- пароль: `passforfoodgram`


  Пользователь Гордон Рамси:

- логин: `gordon@ramsey.com`
- пароль: `passforgordon`

### Применнённые в проекте решения:
Адаптированная к проекту модель пользователя взята из статьи [Customizing Django Authentication using AbstractBaseUser](https://dev.to/joshwizzy/customizing-django-authentication-using-abstractbaseuser-llg).

Для загрузки изображений закодированных в формате *base64* использована библиотека [drf-extra-fields](https://github.com/Hipo/drf-extra-fields).

Для Тэгов использована библиотека [django-colorfield](https://github.com/fabiocaccamo/django-colorfield) позволяющая в интерфейсе админ панели выбирать цвет тэга при помощи color-picker'a.

Для регистрации и аутентификации использована библиотека [djoser](https://github.com/sunscrapers/djoser).

### Запуск проекта на локальной машине.

- Клонировать репозиторий, перейти в директорию *infra* и запустить контейнеры:
```
> git clone https://github.com/kurtKostein/foodgram-project-react.git
```

- В директории *backend* создать файл _.env_ и наполнить его содержимым по анологии с файлом _.env.example_.
```
> cd infra
> docker-compose up
```
- Далее, провести миграции, создать суперпользователя, собрать статику:
```
> docker-compose exec <<название контейнера>> python manage.py migrate --noinput
> docker-compose exec <<название контейнера>> python manage.py createsuperuser
> docker-compose exec <<название контейнера>> python manage.py collectstatic --no-input  
```
- Загрузить данные из директории *data*:
```
> cat <<fixture_name.json>> | sudo docker exec -i <<container_name_or_id>> python manage.py loaddata --format=json -
```

Для локальной работы над проектом, в файле [docker-compose.override.yml](infra/docker-compose.override.yml) 
переопределены некоторые директивы, например применена сборка контейнера вместо его загрузки 
с **DockerHub**, используется _local_nginx.conf_ вместо _nginx.conf_, а так же иное расположение _.env_ файла.


![парам-пам-пам](https://cs12.pikabu.ru/post_img/big/2020/08/24/3/1598236717197322430.png)
