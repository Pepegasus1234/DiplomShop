Все необходимые пэкэджи pip для установки:

pip freeze --all
asgiref==3.8.1
certifi==2025.1.31
charset-normalizer==3.4.1
coverage==7.6.12
Deprecated==1.2.18
distro==1.9.0
Django==5.1.4
idna==3.10
mysqlclient==2.2.7
netaddr==1.3.0
pillow==11.1.0
pip==24.3.1
requests==2.32.3
sqlparse==0.5.3
tzdata==2024.2
urllib3==2.3.0
wrapt==1.17.2
yookassa==3.5.0

Необходимо выполнить pip install yookassa, asgiref, certifi, charset-normalizer, coverage, Deprecated, Django, idna, mysqlclient, netaddr, pillow, requests, sqlparse, tzdata, urllib3, wrapt, yookassa перед запуском
Затем запускаем проект через python -m manage.py makemigrations для заполнения БД всеми моделями через ORM
python -m manage.py migrate
python -m manage.py runserver
Сервер с приложением будет запушен на http://localhost:8000/
