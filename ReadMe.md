- ilk olarak data klasörünün içerisindekileri bir dış katmana taşımak gerekiyor


    sudo mv data/* ../data/


- data klasörünün içerisindeki filtered_hotel_reviews, filtered_hotel_reviews2, filtered_hotel_reviews3 ben istek atıp gelenleri kayıt ediyorum


- diğer iki filtered_hotel_reviewsler içinde istek atıp kayıt etmek için **"config.yaml"** dan aşağıdaki "**HOTEL_DF_PATH**" ve "**REVIEWS_OUTPUT_PATH**" ı değiştirmek gerekmektedir

    
    USER_AGENTS_PATH : "data/user-agents.json"
    HOTEL_DF_PATH : "data/filtered_hotel_review_links<?>.csv"
    REVIEWS_OUTPUT_PATH : "data/review<?>.json"

- docker'ı build edip run edebiliriz buradan sonra istekler otomatik olarak belirtilen  "**REVIEWS_OUTPUT_PATH**" a kayıt edilecektir


    docker build -t scrapper .
    docker run  -d -v "/home/ubuntu/data:/app/data" --name scrapper scrapper