FROM python:3

MAINTAINER Ryunseok Kim <ryunseok@gmail.com>

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app
CPPY ./appcode/ .

CMD ["python", "./app.py"]


