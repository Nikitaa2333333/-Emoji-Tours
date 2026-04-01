
import os
import re
from bs4 import BeautifulSoup

file_path = r'c:\Users\User\Downloads\tilda dododo\content_extracted\тильда.txt'
output_path = r'c:\Users\User\Downloads\tilda dododo\content_extracted\тильда_структура.md'

def normalize_case(text):
    text = text.strip()
    if text.isupper() and len(text) > 3:
        return text.capitalize()
    return text

def is_all_caps(text):
    clean_text = re.sub(r'[^А-ЯЁA-Z]', '', text)
    return text.isupper() and len(clean_text) > 3

def extract_tilda_structure():
    if not os.path.exists(file_path):
        print(f"Ошибка: Файл {file_path} не найден!")
        return

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    # Используем селектор, который найдет любой блок с этими классами
    records = soup.select('div.r.t-rec')
    
    if not records:
        print("Предупреждение: Блоки 'div.r.t-rec' не найдены. Пробую альтернативный поиск...")
        records = soup.find_all('div', id=re.compile(r'^rec'))

    structured_content = []

    for record in records:
        # 1. Заголовки полей Title
        title_tag = record.find(attrs={"field": "title"})
        if title_tag:
            txt = title_tag.get_text().strip()
            if txt:
                # В заголовках title часто 24px не пишут, они и так заголовки
                structured_content.append(f"[H1] # {normalize_case(txt)}")

        # 2. Текстовые поля
        text_field = record.find(attrs={"field": "text"})
        if not text_field:
            continue

        # Сначала обрабатываем все STRONG внутри
        for strong in text_field.find_all('strong'):
            style = strong.get('style', '')
            content = strong.get_text().strip()
            if not content: continue
            
            # ПРАВИЛО: Только 24px = H1. Капс сам по себе не заголовок.
            if '24px' in style:
                strong.replace_with(f"\n---H1MARKER--- {content}\n")
            else:
                # Обычный жирный
                strong.replace_with(f"**{content}**")
        
        # Теперь разбиваем текст на строки
        # Заменяем <br> на переносы
        for br in text_field.find_all('br'):
            br.replace_with("\n")
            
        lines = text_field.get_text().split("\n")
        for line in lines:
            line = line.strip()
            if not line: continue
            
            if '---H1MARKER---' in line:
                header_text = line.replace('---H1MARKER---', '').strip()
                structured_content.append(f"[H1] # {normalize_case(header_text)}")
            else:
                # Буллиты
                if line.startswith('●') or line.startswith('•'):
                    line = "- " + line[1:].strip()
                structured_content.append(line)

    # Итоговая сборка
    final_output = []
    for item in structured_content:
        if item.startswith('[H1]'):
            final_output.append(f"\n{item}\n")
        else:
            final_output.append(item)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# FINAL MEGA PARSER v7\n\n")
        f.write("\n".join(final_output))

    print(f"Успех! Обработано блоков: {len(records)}")
    print(f"Результат в: {output_path}")

if __name__ == "__main__":
    extract_tilda_structure()
