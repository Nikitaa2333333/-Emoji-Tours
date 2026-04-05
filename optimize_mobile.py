import os
import re

def optimize_file(path):
    print(f"Обработка {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Списки замен (Типографика + Цвет)
    replacements = [
        # Типографика (мобильные адаптации)
        (r'(?<![:-])\btext-6xl\b', 'text-4xl md:text-8xl'),
        (r'(?<![:-])\btext-3xl\b', 'text-2xl md:text-5xl'),
        (r'(?<![:-])\btext-xl\b', 'text-base md:text-xl'),
        (r'(?<![:-])\bmb-24\b', 'mb-12 md:mb-24'),
        (r'(?<![:-])\bspace-y-16\b', 'space-y-10 md:space-y-16'),
        
        # Черный цвет везде (удаление прозрачности и серого)
        (r'\btext-black\/[0-9]+\b', 'text-black'),  # text-black/80, text-black/40 и т.д.
        (r'\btext-on-surface-variant\b', 'text-black'),
        (r'\btext-on-surface\b', 'text-black'),
        (r'rgba\(0,\s*0,\s*0,\s*0\.[0-9]+\)', 'rgb(0, 0, 0)'), # Замена в стилях
        (r'color:\s*#888', 'color: #000'), # Замена серых цветов в инлайнах
        (r'color:\s*rgba\(0,\s*0,\s*0,\s*0\.4\)', 'color: #000'),
    ]

    new_content = content
    for pattern, replacement in replacements:
        new_content = re.sub(pattern, replacement, new_content)

    # Очистка дубликатов классов (md:text-8xl md:text-8xl)
    new_content = re.sub(r'\b(md:[^\s"\'}]+)\s+\1\b', r'\1', new_content)
    
    # Также уберем прозрачность в tailwind config если она там есть для констант
    if "tailwind.config" in new_content:
        new_content = new_content.replace('"on-surface-variant": "#000000"', '"on-surface-variant": "#000000"') # уже черный

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
        r'templates',
        '.' # Текущая папка для index.html
    ]
    
    for directory in base_dirs:
        if not os.path.exists(directory):
            continue
            
        print(f"\n--- Сканирование директории: {directory} ---")
        items = os.listdir(directory) if directory != '.' else ['index.html']
        for filename in items:
            if filename.endswith(".html"):
                path = os.path.join(directory, filename)
                if os.path.isfile(path):
                    optimize_file(path)

if __name__ == "__main__":
    process_directories()
    print("\nОптимизация мобильной типографики и установка черного цвета завершена!")
