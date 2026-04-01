import os, glob, re

# Тот же мэппинг для ссылок
SLUGS = {
    "Испания": "spain", "Италия": "italy", "Мексика": "mexico", "Индия": "india",
    "Шри-Ланка": "sri-lanka", "Тунис": "tunisia", "Индонезия": "indonesia",
    "Вьетнам": "vietnam", "Куба": "cuba", "Израиль": "israel", "Доминикана": "dominicana",
    "ОАЭ": "uae", "Кипр": "cyprus", "Таиланд": "thailand", "Египет": "egypt",
    "Турция": "turkey", "Китай": "china", "Танзания": "tanzania", "Маврикий": "mauritius",
    "Сейшелы": "seychelles", "Мальдивы": "maldives"
}

def get_country_data():
    data = []
    files = glob.glob("content_extracted/*.txt")
    for f_path in files:
        name = os.path.basename(f_path).replace(".txt", "")
        if "Памятка" in name or name == "_summary_map": continue
        
        hero = ""
        with open(f_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("HERO_PHOTO:"):
                    hero = line.replace("HERO_PHOTO:", "").strip()
                    break
        
        slug = SLUGS.get(name, name.lower())
        data.append({"name": name, "hero": hero, "url": f"{slug}.html"})
    return sorted(data, key=lambda x: x['name'])

def update_index():
    countries = get_country_data()
    
    # Шаблон карточки
    card_tpl = """
    <a href="{url}" class="block relative group h-[400px] overflow-hidden card-asymmetric cursor-pointer shadow-lg">
        <img class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" src="{hero}" alt="{name}">
        <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-60"></div>
        <div class="absolute bottom-6 left-6 text-white space-y-1">
            <p class="text-xs font-bold tracking-widest uppercase opacity-70">Направление</p>
            <h3 class="text-2xl font-bold">{name}</h3>
        </div>
    </a>"""

    grid_content = "\n".join([card_tpl.format(**c) for c in countries])

    index_path = "index.html"
    if not os.path.exists(index_path):
        print(f"Error: {index_path} not found")
        return

    with open(index_path, "r", encoding='utf-8') as f:
        content = f.read()

    # Ищем сетку стран и заменяем её содержимое
    pattern = r'(<!-- Bento Grid of Countries -->\s*<div[^>]*>).*?(<!-- Questionnaire Section -->)'
    
    # Мы ищем div и заменяем его содержимое до следующей секции
    new_content = re.sub(pattern, 
                        r'\1\n' + grid_content + r'\n</div>\n</div>\n</section>\n\2', 
                        content, 
                        flags=re.DOTALL)

    with open(index_path, "w", encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Главная страница обновлена! Добавлено стран: {len(countries)}")

if __name__ == "__main__":
    update_index()
