FROM python:3.6-slim

WORKDIR /usr/src/tibber_web

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./dash_app/index.py" ]