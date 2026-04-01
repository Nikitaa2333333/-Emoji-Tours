import os
import re

def fix_country_files():
    countries_dir = os.path.join('pages', 'countries')
    
    if not os.path.exists(countries_dir):
        print(f"Ошибка: Директория {countries_dir} не найдена.")
        return

    for filename in os.listdir(countries_dir):
        if filename.endswith('.html'):
            file_path = os.path.join(countries_dir, filename)
            slug = filename.replace('.html', '')
            print(f"Исправление: {filename}...")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 1. Исправление путей к лого и главной
            content = content.replace('href="index.html"', 'href="../../index.html"')
            content = content.replace('src="images/LogoB_300x.png"', 'src="../../images/LogoB_300x.png"')
            
            # 2. Исправление ссылок в футере
            content = re.sub(r'href="index.html#(.*?)"', r'href="../../index.html#\1"', content)
            
            # 3. Исправление ссылки на памятку (переход в pages/memos/)
            # Ищем ссылки вида memo-egypt.html или просто ссылку с текстом "Памятка туристу"
            content = re.sub(r'href="memo-.*?\.html"', f'href="../memos/{slug}.html"', content)
            
            # На случай если ссылка была уже исправлена частично или имеет другой формат
            if f'href="../memos/' not in content:
                 content = content.replace('href="Памятка туристу"', f'href="../memos/{slug}.html"')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

    print("\nВсе страницы стран успешно стандартизированы!")

if __name__ == "__main__":
    fix_country_files()
