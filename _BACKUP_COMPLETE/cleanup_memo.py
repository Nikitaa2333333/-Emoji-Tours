import os
import re

def clean_memo_file(filepath):
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Удаляем ссылку из бокового меню
    link_pattern = r'<a\s+href="#section-turistam-vyezzhayuschim-v-[^"]+"\s+class="nav-link">[^<]*Туристам,\s+выезжающим\s+в[^<]*</a>'
    content = re.sub(link_pattern, '', content, flags=re.IGNORECASE)

    # 2. Удаляем весь блок <section>, содержащий заголовок "Туристам, выезжающим в..."
    # Ищем <section ...> ... Туристам, выезжающим в ... </section>
    # Используем нежадный поиск .*? и флаг DOTALL
    section_pattern = r'<section[^>]*>[^<]*<(h[1-2])[^>]*>[^<]*Туристам,\s+выезжающим\s+в[^<]*</\1>.*?</section>'
    content = re.sub(section_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)

    # 3. На всякий случай удаляем просто заголовок, если он был не в section
    header_pattern = r'<(h[1-2])[^>]*>[^<]*Туристам,\s+выезжающим\s+в[^<]*</\1>'
    content = re.sub(header_pattern, '', content, flags=re.IGNORECASE)
    
    # 4. Удаляем пустые секции, если они остались (на всякий случай)
    empty_section_pattern = r'<section[^>]*>\s*</section>'
    content = re.sub(empty_section_pattern, '', content, flags=re.IGNORECASE)

    # 5. Убираем лишние переносы строк
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    files = [f for f in os.listdir('.') if f.startswith('memo-') and f.endswith('.html')]
    for f in files:
        clean_memo_file(f)
    print("\nГотово! Лишние линии и заголовки удалены.")

if __name__ == "__main__":
    main()
