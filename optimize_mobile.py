import os
import re

def optimize_file(path):
    print(f"Обработка {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Таблица замен согласно ТЗ
    replacements = [
        (r'\btext-6xl\b', 'text-4xl md:text-8xl'),
        (r'\btext-3xl\b', 'text-2xl md:text-5xl'),
        (r'\btext-xl\b', 'text-base md:text-xl'),
        (r'\bmb-24\b', 'mb-12 md:mb-24'),
        (r'\bspace-y-16\b', 'space-y-10 md:space-y-16')
    ]

    new_content = content
    for pattern, replacement in replacements:
        # Используем regex для замены только целых классов
        new_content = re.sub(pattern, replacement, new_content)

    # Очистка дубликатов, если они возникли (напр. md:text-8xl md:text-8xl)
    # Ищем повторяющиеся группы классов с префиксом md:
    new_content = re.sub(r'\b(md:[^\s"\'}]+)\s+\1\b', r'\1', new_content)

    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  - Готово (внесены изменения)")
    else:
        print(f"  - Без изменений")

def process_directories():
    base_dirs = [
        r'pages',
        r'pages\memos',
        r'pages\countries',
        r'templates'
    ]
    
    for directory in base_dirs:
        if not os.path.exists(directory):
            continue
            
        print(f"\n--- Сканирование директории: {directory} ---")
        for filename in os.listdir(directory):
            if filename.endswith(".html"):
                optimize_file(os.path.join(directory, filename))

if __name__ == "__main__":
    process_directories()
    print("\nОптимизация мобильной типографики завершена!")
