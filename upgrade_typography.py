import os
import glob
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. Заменяем стили текста ВЕЗДЕ внутри атрибута class, 
    # независимо от того, какие отступы (mb-8, pt-1, pb-4) идут до или после.
    # Это захватит и обычные абзацы, и пункты списков (буллиты).
    content = content.replace(
        "text-2xl leading-relaxed text-on-surface-variant font-light",
        "text-lg md:text-xl leading-relaxed text-black font-normal"
    )

    # На всякий случай обрабатываем варианты, если где-то порядок классов чуть другой
    # (Например, если в списках остался просто text-2xl font-light)
    content = re.sub(
        r'text-2xl\s+text-on-surface-variant\s+font-light',
        'text-lg md:text-xl text-black font-normal',
        content
    )

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[+] Списки и тексты исправлены: {os.path.basename(filepath)}")

def main():
    print("Вторая итерация: обновляю пункты списков и кастомные блоки...")
    html_files = glob.glob("*.html")
    skip_files = ["index.html", "dashboard.html"]
    
    updated_count = 0
    for file in html_files:
        if file in skip_files:
            continue
        
        with open(file, 'r', encoding='utf-8') as f:
            c = f.read()
            
        process_file(file)
        
        with open(file, 'r', encoding='utf-8') as f:
            if c != f.read():
                updated_count += 1

    print(f"\nГотово! Докрутили файлов: {updated_count}")
    print("Теперь и списки с галочками выглядят идеально.")

if __name__ == "__main__":
    main()
