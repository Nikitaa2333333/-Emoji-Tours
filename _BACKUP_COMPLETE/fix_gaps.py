import os
import re

# Настройки
TARGET_DIR = r"c:\Users\User\Downloads\tilda dododo"

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. Уменьшаем огромные вертикальные отступы между секциями
    # space-y-32 -> space-y-16
    content = content.replace('space-y-32', 'space-y-16')
    
    # 2. Уменьшаем паддинг внутри секций с разделителем
    # pt-24 border-t -> pt-12 border-t
    content = content.replace('pt-24 border-t', 'pt-12 border-t')
    
    # 3. Уменьшаем отступ после кнопок "Хочу туда / Памятка"
    # mb-24 -> mb-10
    content = content.replace('mb-24', 'mb-10')
    
    # 4. Уменьшаем отступ после основного заголовка H1
    # mb-12 -> mb-8
    content = content.replace('mb-12">', 'mb-8">')
    
    # 5. Исправляем лишний верхний отступ в памятках (template_memo.html и производные)
    # pt-32 на контейнере + py-20 на контенте = слишком много.
    # Убираем pt-32, оставляем только py-20 (80px), что достаточно для фикс. шапки.
    content = content.replace('gap-12 pt-32', 'gap-12 pt-20')
    
    # 6. Уменьшаем отступ между фото и текстом внутри секций
    # space-y-8 -> space-y-6
    content = content.replace('space-y-8', 'space-y-6')
    
    # 7. Уменьшаем отступ h2 снизу
    # mb-16 -> mb-8
    content = content.replace('mb-16', 'mb-8')

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("🧹 Очистка лишних отступов (Gap Fix)...")
    html_files = [f for f in os.listdir(TARGET_DIR) if f.endswith('.html')]
    
    updated = 0
    for filename in html_files:
        filepath = os.path.join(TARGET_DIR, filename)
        if process_file(filepath):
            updated += 1
            print(f"✅ Исправлено: {filename}")
        else:
            print(f"➖ Без изменений: {filename}")

    print(f"\n🎉 Готово! Отступы оптимизированы в {updated} файлах.")

if __name__ == "__main__":
    main()
