FROM python:3.11.1

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app

ENV TZ=Europe/Rome

EXPOSE 6000

CMD ["python3", "-u" , "application.py"]