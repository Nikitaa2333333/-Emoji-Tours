import os
import re
from bs4 import BeautifulSoup

MEMOS_DIR = r"c:\Users\User\Downloads\tilda dododo\pages\memos"
TILDA_DIR = r"c:\Users\User\Downloads\tilda dododo\tilda_raw\emojitours.ru"

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^а-яa-z0-9\s]+', ' ', text)
    return " ".join(text.split())

def index_tilda_for_real(file_path):
    index = []
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        recs = soup.find_all('div', class_='t-rec')
        last_important_text = ""
        for r in recs:
            raw_text = r.get_text(separator=" ").strip()
            if len(raw_text) > 5 and "google" not in raw_text.lower():
                last_important_text = clean_text(raw_text)
            imgs = r.find_all('img', class_='t-img')
            for img in imgs:
                src = img.get('data-original') or img.get('src')
                if src and "lib__icons" not in src:
                    if len(last_important_text) > 10:
                        anchor = last_important_text[:35] if len(last_important_text) > 35 else last_important_text
                        index.append({"anchor": anchor, "src": src})
    return index

def find_best_tilda_file(country_name):
    """ Ищет лучший файл Тильды для страны (приоритет версиям с 'Памятка') """
    candidates = []
    c_name_lower = country_name.lower()
    
    # Варианты для Таиланда
    search_names = [c_name_lower]
    if c_name_lower == "тайланд": search_names.append("таиланд")
    if c_name_lower == "таиланд": search_names.append("тайланд")

    for filename in os.listdir(TILDA_DIR):
        if filename.startswith("page") and filename.endswith(".html"):
            path = os.path.join(TILDA_DIR, filename)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read(2000).lower() # Ищем в заголовке
                    for sn in search_names:
                        if sn in content:
                            score = 1
                            if "памятка" in content: score = 10 # Приоритет памяткам
                            candidates.append((score, path))
            except: continue
    
    if not candidates: return None
    # Возвращаем лучший по скорингу
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]

def smart_inject():
    countries = {
        "egypt": "Египет", "maldives": "Мальдивы", "china": "Китай", 
        "turkey": "Турция", "uae": "ОАЭ", "thailand": "Тайланд",
        "seychelles": "Сейшелы", "sri-lanka": "Шри-Ланка", "cuba": "Куба",
        "indonesia": "Индонезия", "mauritius": "Маврикий", "tanzania": "Танзания",
        "tunisia": "Тунис", "vietnam": "Вьетнам"
    }

    print("--- Умная привязка фото (Фиксим соответствие стран) ---")
    
    for slug, c_name in countries.items():
        memo_path = os.path.join(MEMOS_DIR, f"{slug}.html")
        if not os.path.exists(memo_path): continue
        
        tilda_file = find_best_tilda_file(c_name)
        if not tilda_file:
            print(f"  ! Файл Тильды для {c_name} не найден")
            continue
            
        print(f"Обработка: {slug}.html (файл: {os.path.basename(tilda_file)})")
        tilda_pics = index_tilda_for_real(tilda_file)
        
        with open(memo_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
        for old in soup.find_all('div', class_='shadow-2xl'): old.decompose()

        inserted_count, used_urls = 0, set()
        for tag in soup.find_all(['h2', 'h3', 'p', 'li']):
            tag_clean = clean_text(tag.text)
            if len(tag_clean) < 5: continue
            for pic in tilda_pics:
                if pic['src'] in used_urls: continue
                if pic['anchor'] in tag_clean or tag_clean in pic['anchor']:
                    container = soup.new_tag('div', attrs={"class": "my-8 overflow-hidden rounded-3xl shadow-2xl"})
                    img = soup.new_tag('img', src=f"../../tilda_raw/emojitours.ru/{pic['src']}", attrs={"class": "w-full h-auto"})
                    container.append(img)
                    tag.insert_after(container)
                    used_urls.add(pic['src'])
                    inserted_count += 1
        
        with open(memo_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"  Готово: Вставлено {inserted_count} фото.")

if __name__ == "__main__":
    smart_inject()
    print("\nПроцесс завершен! Теперь всё на своих местах.")
