FROM --platform=linux/amd64 python:3.7-slim

WORKDIR /backend

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip
RUN pip3 install -r requirements.txt --no-cache-dir

COPY . ./

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]