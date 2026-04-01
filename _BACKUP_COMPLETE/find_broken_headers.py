import os
import re

# Список слов, которые МОГУТ быть заголовками (даже если короткие)
VALID_HEADERS = [
    "Время", "Климат", "Валюта", "Язык", "Население", "Религия", 
    "Обычаи", "Транспорт", "Телефон", "В отеле", "Кухня", "Магазины",
    "Виза", "Связь", "Деньги", "Погода", "О стране", "Внимание", "Итого"
]

def find_technical_headers(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Ищем все H2 внутри контентной области
    # Обычно они выглядят так: <h2 id="section-..." class="...">Текст</h2>
    pattern = r'<h2 id="section-[^>]*class="[^>]*">(.*?)</h2>'
    matches = re.finditer(pattern, content, flags=re.IGNORECASE | re.DOTALL)
    
    found = []
    for m in matches:
        text = m.group(1).strip()
        clean_text = re.sub('<[^>]*>', '', text) # убираем теги
        
        # Если текст слишком длинный — это вряд ли "значение", пропускаем
        if len(clean_text) > 60:
            continue
            
        # Условия "подозрительности":
        is_suspicious = False
        
        # 1. Содержит цифры (телефон, часы работы, курс валют)
        if any(char.isdigit() for char in clean_text) and clean_text not in VALID_HEADERS:
            is_suspicious = True
        
        # 2. Содержит собачку (email)
        if '@' in clean_text:
            is_suspicious = True
            
        # 3. Очень короткое слово (например, "Ислам", "Рупии"), которое не входит в список разрешенных заголовков
        if len(clean_text) < 20 and clean_text not in VALID_HEADERS:
            # Проверяем, нет ли этого слова в списке валидных заголовков
            if not any(valid.lower() in clean_text.lower() for valid in VALID_HEADERS):
                is_suspicious = True

        if is_suspicious:
            found.append(clean_text)
    
    return found

def main():
    files = [f for f in os.listdir('.') if f.startswith('memo-') and f.endswith('.html')]
    print(f"--- ПОИСК ТЕХНИЧЕСКИХ ЗАГОЛОВКОВ (H2, которые должны быть P) ---")
    total_found = 0
    
    for file in files:
        matches = find_technical_headers(file)
        if matches:
            print(f"\n[{file}]")
            for text in matches:
                print(f"  ⚠️ Подозрительный H2: {text}")
                total_found += 1
    
    print(f"\n----------------------")
    print(f"Всего найдено: {total_found}")

if __name__ == "__main__":
    main()
