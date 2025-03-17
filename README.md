# 0. Зависимости необходимые перед установкой

## 0.1. Установка python 3.14 :snake:	
https://www.python.org/downloads/

## 0.2. Установка зависимостей через pip
>Мог бы скомпоновать все в докер имэдж но возникает проблема при настройке docker-network за NAT во время обращения к API юкассы при пробросе портов на марше :disappointed:, POST'ы от юкассы проходят в бридж нетворк, но при маршрутизации от бриджа улетают в другой порт маршрутизатора, которой в NAT таблице нет

$${\color{lightblue}pip freeze --all}$$	<br/>
asgiref==3.8.1 <br/>
certifi==2025.1.31 <br/>
charset-normalizer==3.4.1 <br/>
coverage==7.6.12 <br/>
Deprecated==1.2.18 <br/>
distro==1.9.0 <br/>
Django==5.1.4 <br/>
idna==3.10 <br/>
mysqlclient==2.2.7 <br/>
netaddr==1.3.0 <br/>
pillow==11.1.0 <br/>
pip==24.3.1 <br/>
requests==2.32.3 <br/>
sqlparse==0.5.3 <br/> 
tzdata==2024.2 <br/>
urllib3==2.3.0 <br/>
wrapt==1.17.2 <br/>
yookassa==3.5.0

Необходимо выполнить <code>pip install yookassa, asgiref, certifi, charset-normalizer, coverage, Deprecated, Django, idna, mysqlclient, netaddr, pillow, requests, sqlparse, tzdata, urllib3, wrapt, yookassa </code>

## 0.3. Установка MySQL Server Community :hash:	
https://dev.mysql.com/downloads/installer/

## 0.4. Настройка БД :gear:
<code>CREATE DATABASE diplom_database;
CREATE USER root@'localhost' IDENTIFIED BY ‘12334’;
GRANT ALL PRIVILEGES ON diplom_database.* TO ‘root@'localhost';
FLUSH PRIVILEGES;</code>

## 0.5. Запуск миграций:
Затем запускаем проект через python -m manage.py makemigrations для заполнения БД всеми моделями через ORM
python -m manage.py migrate

## 0.6. Проброс портов из локальной сети на белый адрес для приема ответов от youkassa (по умолчанию после установки соединения Django закрывает порт, поэтому необходимо статически забиндить порт):
![image](https://github.com/user-attachments/assets/e66b97d2-eaed-48c8-9311-16f0d273c16a)

# 1. Запуск сервера:
python -m manage.py runserver
Сервер с приложением будет запущен на http://localhost:8000/

# 2. Функционал приложения:
## 2.0 Функционал не зарегестрированного польз.
Пользователя встречает хоумпейдж:
![image](https://github.com/user-attachments/assets/d05bae2f-cba5-4b3d-8534-dab194a762b6)
Можно перейти в каталог, по умолчанию если ни один продавец не добавил товар предложения отсутствуют:
![image](https://github.com/user-attachments/assets/14337cd2-19f5-44d4-81e8-3a0f07dcb847)

## 2.1 Регистрация авторизация:
На авторизацию, попадаем из хедер панели сверху справа по кнопке LOGIN:

![image](https://github.com/user-attachments/assets/655d8494-fc52-49db-bc21-aa31be7513b3)

Нажатием на кнопку регистрации в кач-ве покупателя продавца попадаем на соответствующие регистрационные страницы:
![image](https://github.com/user-attachments/assets/8968c01b-8c13-48d9-a488-f156a53d410b) ![image](https://github.com/user-attachments/assets/c5f9dd23-cd60-4f1a-8872-1af354f01942)

При регистрации нас редиректит на хоумпейдж после чего авторизуемся 

## 2.2 Функционал продавца:
После авторизацции в качестве продавца происходит редирект на личный кабинет, слева есть панель навигации справа рабочая область

![image](https://github.com/user-attachments/assets/b687ac82-c8f3-4e36-a6e4-f9e864468594)
> Мой профиль вкладка с информацией
![image](https://github.com/user-attachments/assets/a8f4d33e-9aeb-42e6-9d7a-0232c183b835)
> Форма смены пароля
![image](https://github.com/user-attachments/assets/ffc2af40-c4fd-4009-8ced-702ee194cfc1)
> Вкладка администрирования
![image](https://github.com/user-attachments/assets/b35b2a87-97b6-4462-97eb-7b83f2958aa2)
> Текущие товары на складе:
![image](https://github.com/user-attachments/assets/0b9ba999-50b1-49b4-9dd6-83be5b306887)
> Добавить товар:
![image](https://github.com/user-attachments/assets/79bcb247-1825-437c-9f31-a9bf93281384)
> Добавить менеджера:
![image](https://github.com/user-attachments/assets/4f8560ab-f6da-4cd2-8a5a-4d08d908eb60)
> Аналитика:
> 
> ![image](https://github.com/user-attachments/assets/653756c2-4fc5-4e82-910e-4c3425e5d95e)

## 2.2 Функционал покупателя:
>Просмотр каталога:
>![image](https://github.com/user-attachments/assets/6e125269-8bd5-429f-a851-2fd42e69eb21)

>Корзина:
>
>![image](https://github.com/user-attachments/assets/5416b56b-bcda-491a-b61f-b1aee1db8ce1)

>Оформления заказа (Интеграция с юкассой):
>![image](https://github.com/user-attachments/assets/2efed2a7-485d-4950-97c3-8a1939125d4e)

>Чаты с продавцами:
>
>![image](https://github.com/user-attachments/assets/cb200055-cdb9-4028-a525-41249e39498e)
>![image](https://github.com/user-attachments/assets/bd46c852-e6dc-4789-8c75-3d1211cf2b24)

>Смена пароля:
>![image](https://github.com/user-attachments/assets/eef2a5fe-aa40-48b7-b5d9-dc07dfa0dbaf)

>Отзывы на товар:
>
>![image](https://github.com/user-attachments/assets/0c7bae55-847d-43e2-996c-64195948a5b3)
