import os
import re

# Настройки
TARGET_DIR = r"c:\Users\User\Downloads\tilda dododo"

# Новые стили для кнопок (Pro Max)
# Желтая кнопка (bg-primary)
YELLOW_BTN_CLASS = (
    "inline-block bg-primary text-black px-10 py-5 rounded-full text-xl font-bold "
    "shadow-xl shadow-[#5f531a]/20 hover:shadow-2xl hover:shadow-[#5f531a]/30 "
    "hover:scale-[1.03] active:scale-95 transition-all"
)

# Черная кнопка (bg-black)
BLACK_BTN_CLASS = (
    "inline-block bg-black text-white px-10 py-5 rounded-full text-xl font-bold "
    "shadow-xl shadow-[#5f531a]/15 hover:shadow-2xl hover:shadow-[#5f531a]/25 "
    "hover:scale-[1.03] active:scale-95 transition-all"
)

# Специальный стиль для кнопок в формах (могут иметь w-full или md:px-14)
FORM_BTN_CLASS = (
    "w-full sm:w-auto bg-black text-white px-10 md:px-14 py-5 rounded-full "
    "text-xl font-bold shadow-xl shadow-[#5f531a]/15 hover:shadow-2xl hover:shadow-[#5f531a]/25 "
    "hover:scale-[1.03] active:scale-95 transition-all flex items-center justify-center"
)

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. Замена кнопок в контенте ("Хочу туда", "Памятка туристу")
    # Ищем по комбинации классов bg-primary/bg-black и px-10 (признак большой кнопки)
    
    # Желтые кнопки
    content = re.sub(
        r'class="[^"]*bg-primary[^"]*px-10[^"]*"',
        f'class="{YELLOW_BTN_CLASS}"',
        content
    )
    
    # Черные кнопки (ссылки)
    content = re.sub(
        r'class="[^"]*bg-black[^"]*px-10[^"]*rounded-full[^"]*"',
        f'class="{BLACK_BTN_CLASS}"',
        content
    )
    
    # 2. Кнопка отправки формы (отдельная логика, так как там часто MD:PX-14)
    content = re.sub(
        r'class="[^"]*bg-black[^"]*type="submit"[^"]*"', # Если класс содержит type="submit" (бывает в старых версиях)
        f'class="{FORM_BTN_CLASS}"',
        content
    )
    # Или просто по тексту внутри кнопки в связке с bg-black
    content = re.sub(
        r'<button([^>]+)class="([^"]*bg-black[^"]*)"([^>]*)>([^<]*(?:Отправить|заявку)[^<]*)</button>',
        f'<button\\1class="{FORM_BTN_CLASS}"\\3>\\4</button>',
        content
    )

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("🚀 Запуск обновления стилей кнопок (Soft Shadows)...")
    html_files = [f for f in os.listdir(TARGET_DIR) if f.endswith('.html')]
    
    updated = 0
    for filename in html_files:
        filepath = os.path.join(TARGET_DIR, filename)
        if process_file(filepath):
            updated += 1
            print(f"✅ Обновлено: {filename}")
        else:
            print(f"➖ Без изменений: {filename}")

    print(f"\n🎉 Готово! Обработано файлов: {len(html_files)}, обновлено: {updated}")

if __name__ == "__main__":
    main()
