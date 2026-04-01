import os
import re

def process_memo(filepath):
    print(f"Обработка: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Заменяем обычный текст на заголовок секции
    # Ищем <p> с текстом "В случае путешествия с детьми или беременности:"
    p_pattern = r'<p[^>]*>\s*В случае\s*путешествия с детьми или беременности:\s*</p>'
    
    # Новая структура секции
    new_header = (
        '</section>\n'
        '<section class="pt-12 border-t border-black/5">\n'
        '    <h2 id="section-deti-i-beremennost" class="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-[1.1] md:leading-none">В случае путешествия с детьми или беременности:</h2>\n'
        '    <div class="space-y-6">'
    )
    
    # Проверяем, есть ли уже такая секция (чтобы не дублировать)
    if 'id="section-deti-i-beremennost"' in content:
        print(f"Секция уже существует в {filepath}")
    else:
        # Заменяем <p> на новый заголовок
        updated_content = re.sub(p_pattern, new_header, content, flags=re.IGNORECASE | re.DOTALL)
        
        if updated_content != content:
            # 2. Добавляем пункт в навигацию (после "Перед отъездом")
            nav_item = '                            <a href="#section-deti-i-beremennost" class="nav-link">Дети и беременность</a>'
            
            # Ищем ссылку "Перед отъездом", чтобы вставить после нее
            nav_pattern = r'(<a href="#section-pered-otezdom"[^>]*>.*?</a>)'
            updated_content = re.sub(nav_pattern, r'\1\n' + nav_item, updated_content, flags=re.IGNORECASE | re.DOTALL)
            
            content = updated_content
            print(f"Обновлено: {filepath}")
        else:
            print(f"Текст не найден в {filepath}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    files = [f for f in os.listdir('.') if f.startswith('memo-') and f.endswith('.html')]
    for f in files:
        process_memo(f)
    print("\nГотово! Все памятки обновлены.")

if __name__ == "__main__":
    main()
