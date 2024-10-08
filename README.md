# aiogram-test

## Описание

TBD


## Требования:
- Python 3 
- aiogram 3.13
- python-dotenv
- и их зависимости (указано в `requirements.txt`)

## Установка на тестовом стенде:

На машине должен быть установлен Python актуальной версии (тестировалось на 3.12)

Клонировать репозиторий на машину, с которой будет будет запускаться сервис (либо по SSH-ссылке, либо скопировать и распаковать zip-архив)

```
git clone https://github.com/andmerk93/aiogram-test.git
```

Перейти в директорию с проектом

```
cd aiogram-test
```

Развернуть виртуальное окружение python в папке с проектом (aiogram-test)

```
python -m venv venv
```

Активировать виртуальное окружение.

Для linux/unix:

```
source ./venv/bin/activate 
``` 

Для Windows, должно быть разрешено выполнение скриптов Powershell:

```
venv\Scripts\activate
``` 

Установить заввисимости:

```
pip install -r requirements.txt
```

Создать файл `.env` из шаблона

```
cp .example.env .env
```

Указать в файле `.env` токен своего бота, в переменной `API_TOKEN`.

Запустить проект:

```
py main.py
```
