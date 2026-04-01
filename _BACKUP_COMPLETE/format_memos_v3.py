import os
import re

def format_memos_v3():
    directory = r'c:\Users\User\Downloads\tilda dododo'
    files = [f for f in os.listdir(directory) if f.startswith('memo-') and f.endswith('.html')]
    
    # 1. Замена текста на секцию
    paragraph_pattern = re.compile(
        r'<p[^>]*>\s*Паспортный\s*контроль\.\s*Виза\.\s*</p>',
        re.IGNORECASE | re.DOTALL
    )
    
    replacement_section = (
        '</div>\n'
        '                    </section>\n'
        '                    <section class="pt-12 border-t border-black/5">\n'
        '                        <h2 id="section-pasportnyj-kontrol-viza" class="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-[1.1] md:leading-none">Паспортный контроль. Виза</h2>\n'
        '                        <div class="space-y-6">'
    )

    # 2. Добавление ссылки в навигацию
    nav_pattern = re.compile(
        r'(<a href="#section-v-aeroportu-prileta-vyleta-[^"]+" class="nav-link">[^<]+</a>)',
        re.IGNORECASE
    )

    for filename in files:
        filepath = os.path.join(directory, filename)
        print(f"Обработка {filename}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Заменяем параграф на секцию
        if paragraph_pattern.search(content):
            new_content = paragraph_pattern.sub(replacement_section, content)
            
            # Добавляем ссылку в навигацию после раздела про аэропорт прилета
            # Ищем ссылку на аэропорт прилета (она может чуть отличаться названием страны)
            match_nav = re.search(r'<a href="#section-v-aeroportu-prileta-vyleta-[^"]+" class="nav-link">[^<]+</a>', new_content)
            if match_nav:
                link = match_nav.group(0)
                new_link = '\n                            <a href="#section-pasportnyj-kontrol-viza" class="nav-link">Паспортный контроль. Виза</a>'
                new_content = new_content.replace(link, link + new_link)
                
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  - Раздел 'Паспортный контроль. Виза' успешно создан и добавлен в меню.")
        else:
            print(f"  - Текст 'Паспортный контроль. Виза' не найден.")

if __name__ == "__main__":
    format_memos_v3()
