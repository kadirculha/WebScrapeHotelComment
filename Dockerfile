FROM python:3.10

# Yazar bilgisi ekle
LABEL authors="kadirculha"

# Çalışma dizinini ayarla
WORKDIR /app

# Gereksinimler dosyasını çalışma dizinine kopyala
COPY requirements.txt .

# Gereksinimleri yükle
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını çalışma dizinine kopyala
COPY . .

# Ana Python dosyasını çalıştır
CMD ["python", "scrape-trip-advisor.py"]

## Docker image oluştur
#docker build -t scrapper .
#
## Docker container başlat ve belirtilen ayarlarla çalıştır
#docker run  -d -v "/home/ubuntu/data:/app/data" --name scrapper scrapper
