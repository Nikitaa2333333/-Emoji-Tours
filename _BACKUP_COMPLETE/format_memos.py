import os
import re

def format_memos():
    directory = r'c:\Users\User\Downloads\tilda dododo'
    files = [f for f in os.listdir(directory) if f.startswith('memo-') and f.endswith('.html')]
    
    # 1. Замена текста на секцию
    # Ищем абзац с текстом "Собирая багаж"
    paragraph_pattern = re.compile(
        r'<p[^>]*>\s*Собирая багаж:?\s*</p>',
        re.IGNORECASE | re.DOTALL
    )
    
    replacement_section = (
        '</div>\n'
        '                    </section>\n'
        '                    <section class="pt-12 border-t border-black/5">\n'
        '                        <h2 id="section-sobiraya-bagazh" class="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-[1.1] md:leading-none">Собирая багаж</h2>\n'
        '                        <div class="space-y-6">'
    )

    # 2. Добавление ссылки в навигацию
    nav_pattern = re.compile(
        r'(<a href="#section-beremennym-zhenschinam" class="nav-link">Беременным женщинам</a>)',
        re.IGNORECASE
    )
    
    nav_replacement = r'\1\n                            <a href="#section-sobiraya-bagazh" class="nav-link">Собирая багаж</a>'

    for filename in files:
        filepath = os.path.join(directory, filename)
        print(f"Обработка {filename}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Заменяем параграф на секцию
        if paragraph_pattern.search(content):
            new_content = paragraph_pattern.sub(replacement_section, content)
            
            # Добавляем ссылку в навигацию
            if nav_pattern.search(new_content):
                new_content = nav_pattern.sub(nav_replacement, new_content)
                
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  - Раздел 'Собирая багаж' успешно создан и добавлен в меню.")
        else:
            print(f"  - Текст 'Собирая багаж' не найден.")

if __name__ == "__main__":
    format_memos()
