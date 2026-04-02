import os
from bs4 import BeautifulSoup

path = r"c:\Users\User\Downloads\tilda dododo\tilda_raw\emojitours.ru"
print(f"--- Сканирую папку: {path} ---")

for f in os.listdir(path):
    if f.startswith("page") and f.endswith(".html"):
        try:
            with open(os.path.join(path, f), "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")
                title = soup.find("title").text if soup.find("title") else "Нет титула"
                print(f"{f}: {title}")
        except Exception as e:
            print(f"Ошибка в файле {f}: {e}")
