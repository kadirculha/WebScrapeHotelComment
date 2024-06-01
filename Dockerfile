FROM python:3.10
LABEL authors="kadirculha"

WORKDIR /app
COPY ./requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını çalışma dizinine kopyala
COPY ./ /app

# Ana Python dosyasını çalıştır
CMD ["python", "scrape-trip-advisor.py"]