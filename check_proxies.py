import threading
import queue
import requests

q = queue.Queue()
valid_proxies = []

with open("proxy-list.txt", "r") as f:
    proxies = f.read().split("\n")
    for p in proxies:
        q.put(p)

def check_proxies():
    global q, valid_proxies
    while not q.empty():
        proxy = q.get()
        try:
            res = requests.get("http://ipinfo.io/json", proxies={"http": proxy, "https": proxy}, timeout=5)
            if res.status_code == 200:
                print(f"{proxy}")
                with open("valid-proxy-list.txt", "a")as f :
                    f.write(f"{proxy}\n")
                valid_proxies.append(proxy)
        except:
            pass

for _ in range(10):
    threading.Thread(target=check_proxies).start()