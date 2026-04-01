import os
import re

# Список заголовков, которые ДОЛЖНЫ оставаться заголовками
VALID_HEADERS = [
    "Перед отъездом", "Собирая багаж", "В Российском аэропорту", "Таможенный контроль",
    "Санитарный контроль", "Ветеринарный контроль", "Регистрация на рейс", 
    "Пограничный контроль", "Внимание", "Посольство", "Консульство", "Экстренные телефоны",
    "Время", "Климат", "Валюта", "Язык", "Население", "Религия", "Обычаи", 
    "Транспорт", "Телефон", "В отеле", "Напряжение электросети", "Экскурсии", 
    "Кухня", "Магазины", "Виза", "Связь", "Деньги", "Погода", "О стране",
    "Полезная информация", "Праздники", "Личная гигиена", "Безопасность",
    "В случае потери паспорта", "Посольство РФ", "Беременным женщинам"
]

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Шаблон для поиска подозрительных H2 в контентной области
    # Ищем: <h2 id="section-..." class="...">Текст</h2>
    pattern = r'(<h2 id="section-[^>]*class="[^>]*">)(.*?)(</h2>)'
    
    def replacer(match):
        prefix = match.group(1)
        text = match.group(2).strip()
        suffix = match.group(3)
        
        clean_text = re.sub('<[^>]*>', '', text)
        
        is_bad = False
        
        # 1. Если это явно почта, телефон или техническая строка
        if '@' in clean_text or 'http' in clean_text:
            is_bad = True
        elif any(char.isdigit() for char in clean_text) and not any(v.lower() in clean_text.lower() for v in VALID_HEADERS):
            # Если есть цифры и это не валидный заголовок (например "год", "день")
            is_bad = True
        elif clean_text.startswith('●') or clean_text.startswith('+'):
            is_bad = True
        elif 'тел.' in clean_text.lower() or 'факс' in clean_text.lower() or 'email' in clean_text.lower():
            is_bad = True
            
        # 2. Если это просто подозрительно короткий текст, не входящий в список разрешенных
        if 0 < len(clean_text) < 40:
            if not any(v.lower() in clean_text.lower() for v in VALID_HEADERS):
                is_bad = True

        if is_bad:
            # Превращаем заголовок H2 в параграф P с соответствующими стилями
            return f'<p class="text-xl leading-relaxed text-black font-normal mb-8">{text}</p>'
        
        return match.group(0)

    # Применяем замену
    new_content = re.sub(pattern, replacer, content, flags=re.IGNORECASE | re.DOTALL)

    if new_content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    files = [f for f in os.listdir('.') if f.startswith('memo-') and f.endswith('.html')]
    print(f"Обработка {len(files)} файлов...")
    count = 0
    for file in files:
        if fix_file(file):
            print(f"✅ Исправлено: {file}")
            count += 1
    
    print(f"\nГотово! Исправлено файлов: {count}")

if __name__ == "__main__":
    main()
