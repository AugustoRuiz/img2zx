FROM python:3.7.7

RUN apt update; apt install -y libgl1

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY src .

ENTRYPOINT [ "python", "./img2zxbasic.py" ]