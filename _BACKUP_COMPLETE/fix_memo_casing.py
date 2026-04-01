import os
import re

# Список слов, которые всегда должны быть с большой буквы (включая склонения, если нужно)
PROPER_NOUNS = [
    "Египет", "Египта", "Кипр", "Кипра", "Китай", "Китая", "Куба", "Кубы", "Доминикана", 
    "Индия", "Индии", "Индонезия", "Индонезии", "Израиль", "Израиля", "Мальдивы", "Мальдив", "Мальдивах",
    "Маврикий", "Мексика", "Мексики", "Сейшелы", "Сейшел", "Шри-Ланка", "Шри-Ланку", 
    "Танзания", "Танзании", "Таиланд", "Таиланда", "Тунис", "Турция", "Турции", "Оаэ", "Вьетнам", "Вьетнама",
    "Россия", "России", "РФ", "Москва", "Москве", "Мале", "Каир", "Никосия", "Пекин", "Гавана", "Дели", 
    "Джакарта", "Иерусалим", "Виктория", "Сингальскому", "Арабского", "Английского", "Ислам"
]

def fix_casing(text):
    if not text:
        return text
    
    # Убираем лишние пробелы
    text = text.strip()
    
    # 1. Первая буква заглавная, остальное не трогаем (так как там уже может быть нормальный текст)
    # Но если текст был совсем в нижнем регистре, надо быть аккуратнее.
    # Большинство текстов сейчас в "нормальном" регистре (после предыдущих замен), но с маленькими именами собственными.
    
    if len(text) > 0:
        text = text[0].upper() + text[1:]
    
    # 2. Исправляем конкретные собственные имена
    for noun in PROPER_NOUNS:
        # Используем boundary \b чтобы не менять части слов
        pattern = re.compile(r'\b' + re.escape(noun) + r'\b', re.IGNORECASE)
        text = pattern.sub(noun, text)
        
    return text

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Исправляем содержимое <h2>
    def replace_h2(match):
        start_tag = match.group(1)
        inner_text = match.group(2)
        end_tag = match.group(3)
        return f"{start_tag}{fix_casing(inner_text)}{end_tag}"

    content = re.sub(r'(<h2[^>]*>)(.*?)(</h2>)', replace_h2, content, flags=re.DOTALL)
    
    # Также исправим ссылки в боковом меню и шторке
    content = re.sub(r'(class="nav-link">)(.*?)(</a>)', replace_h2, content, flags=re.DOTALL)
    content = re.sub(r'(class="nav-link-item"><span>)(.*?)(</span>)', replace_h2, content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Исправлен регистр в: {file_path}")

def main():
    for filename in os.listdir("."):
        if filename.startswith("memo-") and filename.endswith(".html"):
            process_file(filename)

if __name__ == "__main__":
    main()
