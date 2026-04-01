import os
import re

def clean_html_files():
    directory = r'c:\Users\User\Downloads\tilda dododo'
    
    # 1. Секция с заголовком (ищем "Все о путешествии" или подобные дубликаты)
    section_regex = re.compile(
        r'<section[^>]*>\s*<h2 id="[^"]+"[^>]*>Все о путешествии.*?</h2>\s*</section>',
        re.DOTALL | re.IGNORECASE
    )
    
    # 2. Ссылка в навигации
    nav_link_regex = re.compile(
        r'<nav id="quick-links"[^>]*>.*?<a href="([^"]+)" class="nav-link">Все о путешествии.*?</a>',
        re.DOTALL | re.IGNORECASE
    )

    # Список файлов для обработки (страны)
    files_to_process = [
        'china.html', 'cuba.html', 'cyprus.html', 'dominicana.html', 'egypt.html',
        'india.html', 'indonesia.html', 'israel.html', 'italy.html', 'maldives.html',
        'mauritius.html', 'mexico.html', 'seychelles.html', 'spain.html', 'sri-lanka.html',
        'tanzania.html', 'thailand.html', 'tunisia.html', 'turkey.html', 'uae.html', 'vietnam.html'
    ]

    for filename in files_to_process:
        filepath = os.path.join(directory, filename)
        if not os.path.exists(filepath):
            print(f"Файл {filename} не найден, пропускаю.")
            continue
            
        print(f"Обработка {filename}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. Удаляем ссылку в навигации (учитывая возможные переносы строк)
        # Регулярка ищет <a> с классом nav-link, внутри которой есть "Все о путешествии"
        content, count_nav = re.subn(
            r'<a[^>]*class="nav-link"[^>]*>\s*Все о путешествии.*?</a>',
            '',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )
        
        # 2. Удаляем секцию с заголовком (учитывая возможные переносы строк)
        content, count_sec = re.subn(
            r'<section[^>]*>\s*<h2 id="[^"]+"[^>]*>\s*Все о путешествии.*?</h2>\s*</section>',
            '',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )
        
        if count_sec > 0 or count_nav > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  - Удалено секций: {count_sec}")
            print(f"  - Удалено ссылок: {count_nav}")
        else:
            print(f"  - Избыточных заголовков не найдено.")

if __name__ == "__main__":
    clean_html_files()
