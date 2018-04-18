FROM python:3

LABEL maintainer "Ryunseok Kim <ryunseok@gmail.com>"

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app
COPY ./appcode/ .

CMD ["python", "./app.py"]


