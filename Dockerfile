FROM python:3.10
# устанавливаем рабочую директорию
WORKDIR /home/www
# устанавливаем переменную окружения для проекта
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean && apt-get install -y vim


RUN pip install --upgrade pip

# Копирование файлов проекта в образ

COPY ./requirements.txt /home/www/requirements.txt
# устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

COPY . /home/www
RUN chmod +x /home/www/entrypoint.sh && chmod -R 755 /home/www
CMD ["/home/www/entrypoint.sh"]
