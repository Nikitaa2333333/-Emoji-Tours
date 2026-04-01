import os
import re

# Это список ЕДИНСТВЕННЫХ разрешенных заголовков. 
# Всё остальное, что помечено как H2, будет разжаловано в обычный текст.
ALLOW_HEADERS = [
    "Перед отъездом", "Собирая багаж", "В Российском аэропорту", "Таможенный контроль",
    "Санитарный контроль", "Ветеринарный контроль", "Регистрация на рейс", 
    "Пограничный контроль", "Внимание", "Важно", "Посольство", "Консульство", "Экстренные телефоны",
    "Время", "Климат", "Валюта", "Язык", "Население", "Религия", "Обычаи", 
    "Транспорт", "Телефон", "В отеле", "Напряжение электросети", "Экскурсии", 
    "Кухня", "Магазины", "Виза", "Связь", "Деньги", "Погода", "О стране",
    "Полезная информация", "Праздники", "Личная гигиена", "Безопасность",
    "В случае потери паспорта", "Беременным женщинам", "Правила ввоза электронных сигарет",
    "Правила ввоза дронов", "Королевство", "В аэропорту", "Паспортный контроль", "По прилете"
]

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    def clean_text(t):
        return re.sub('<[^>]*>', '', t).strip()

    # Паттерн для поиска ЛЮБЫХ H2 с section-ID
    pattern = r'<h2 id="(section-[^"]*)"[^>]*>(.*?)</h2>'
    
    def replacer(match):
        full_tag = match.group(0)
        text = match.group(2)
        inner_text = clean_text(text)
        
        # Если текст заголовка НЕ содержит ни одного слова из списка разрешенных — это ошибка.
        # Также, если он заканчивается на ";" или слишком длинный — это точно не заголовок раздела.
        is_valid = False
        for allowed in ALLOW_HEADERS:
            if allowed.lower() in inner_text.lower():
                is_valid = True
                break
        
        # Если это точно пункт списка (заканчивается на ;) или не прошел проверку
        if not is_valid or inner_text.endswith(';') or len(inner_text) > 80:
            return f'<p class="text-xl leading-relaxed text-black font-normal pt-1">{text}</p>'
        
        return full_tag

    new_content = re.sub(pattern, replacer, content, flags=re.IGNORECASE | re.DOTALL)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    files = [f for f in os.listdir('.') if f.startswith('memo-') and f.endswith('.html')]
    print(f"🚀 Полная чистка заголовков в {len(files)} файлах...")
    for file in files:
        if fix_file(file):
            print(f"✅ Очищен: {file}")
    print("\n✨ Готово! Все лишние заголовки убраны.")

if __name__ == "__main__":
    main()