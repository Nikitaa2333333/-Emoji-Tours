import os
import re
from bs4 import BeautifulSoup

# ПУТИ
MEMOS_DIR = r"c:\Users\User\Downloads\tilda dododo\pages\memos"
TILDA_DIR = r"c:\Users\User\Downloads\tilda dododo\tilda_raw\emojitours.ru"

def get_full_tilda_map(country_name):
    """ Собирает ПОЛНУЮ карту всех картинок со страницы Тильды """
    # Карта: заголовок -> список URL
    content_map = {"intro": []}
    
    # Пытаемся найти подходящий файл
    target_file = None
    for filename in os.listdir(TILDA_DIR):
        if not filename.startswith("page") or not filename.endswith(".html"): continue
        path = os.path.join(TILDA_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            title = soup.find('title').text if soup.find('title') else ""
            # Более гибкий поиск (Куба -> Кубу и т.д.)
            if country_name.lower()[:3] in title.lower():
                target_file = path
                break
    
    if not target_file: return None

    with open(target_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        recs = soup.find_all('div', class_='t-rec')
        
        current_hdr = "intro"
        for r in recs:
            # Ищем заголовок
            tf = r.find('div', field='text')
            if tf:
                h = tf.find('strong')
                if h and len(h.text.strip()) > 3:
                    new_hdr = h.text.strip().lower()
                    if new_hdr not in content_map: content_map[new_hdr] = []
                    current_hdr = new_hdr
            
            # Ищем ВСЕ картинки в этом блоке
            imgs = r.find_all('img', class_='t-img')
            for img in imgs:
                src = img.get('data-original') or img.get('src')
                if src and "lib__icons" not in src:
                    content_map[current_hdr].append(src)
                    
    return content_map

def inject():
    countries = {
        "egypt": "Египет", "maldives": "Мальдивы", "china": "Китай", 
        "turkey": "Турция", "uae": "ОАЭ", "thailand": "Тайланд",
        "seychelles": "Сейшелы", "sri-lanka": "Шри-Ланка", "cuba": "Куба",
        "indonesia": "Индонезия", "mauritius": "Маврикий", "tanzania": "Танзания",
        "tunisia": "Тунис", "vietnam": "Вьетнам"
    }

    print("--- Глубокая вставка ВСЕХ фото из Тильды ---")
    
    for slug, c_name in countries.items():
        file_path = os.path.join(MEMOS_DIR, f"{slug}.html")
        if not os.path.exists(file_path): continue
        
        print(f"Обработка: {slug}.html...")
        
        tilda_data = get_full_tilda_map(c_name)
        if not tilda_data:
            print(f"  ! Страница для {c_name} не найдена.")
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # 1. Удаляем любые старые hero-блоки или пустые места
        for old_hero in soup.find_all('div', class_='h-[40vh]'): old_hero.decompose()
        
        # 2. Вставляем интро-фотки (если есть) СРАЗУ ПОСЛЕ заголовка H1
        intro_imgs = tilda_data.get("intro", [])
        if intro_imgs:
            h1 = soup.find('h1')
            if h1:
                # Вставляем их снизу вверх, чтобы они шли по порядку
                for src in reversed(intro_imgs):
                    container = soup.new_tag('div', attrs={"class": "mb-10 overflow-hidden rounded-3xl shadow-2xl"})
                    img = soup.new_tag('img', src=f"../../tilda_raw/emojitours.ru/{src}", attrs={"class": "w-full h-auto"})
                    container.append(img)
                    h1.insert_after(container)

        # 3. Вставляем фотки в разделы
        h2_tags = soup.find_all('h2')
        total_injected = len(intro_imgs)
        
        for h2 in h2_tags:
            txt = h2.text.strip().lower()
            # Пытаемся найти совпадение заголовка
            section_imgs = []
            for t_hdr, imgs in tilda_data.items():
                if t_hdr in txt or txt in t_hdr:
                    section_imgs.extend(imgs)
            
            if section_imgs:
                # Вставляем все найденные фото для этого раздела
                for src in reversed(list(dict.fromkeys(section_imgs))): # Убираем дубли и вставляем по порядку
                    container = soup.new_tag('div', attrs={"class": "mb-10 overflow-hidden rounded-3xl shadow-2xl"})
                    img = soup.new_tag('img', src=f"../../tilda_raw/emojitours.ru/{src}", attrs={"class": "w-full h-auto"})
                    container.append(img)
                    h2.insert_after(container)
                    total_injected += 1
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"  Готово: Вставлено {total_injected} фото.")

if __name__ == "__main__":
    inject()
    print("\nТеперь абсолютно все фото из Тильды перенесены!")
