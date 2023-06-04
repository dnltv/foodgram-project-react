FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . .
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]
LABEL author='https://github.com/dnltv'
