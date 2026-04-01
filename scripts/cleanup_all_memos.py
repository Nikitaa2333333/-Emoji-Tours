
import os
import re

folder_path = r'c:\Users\User\Downloads\tilda dododo\content_extracted'

def normalize_case(text):
    if text.isupper() and len(text) > 3:
        return text.capitalize()
    return text

def cleanup_file(filepath):
    # Читаем содержимое
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    new_lines = []
    skipped = False
    
    for line in lines:
        cleaned_line = line.strip()
        # Пропускаем строку, если в ней есть "Туристам, выезжающим в"
        if "Туристам, выезжающим в" in cleaned_line:
            skipped = True
            continue
        
        # Если строка - заголовок Маркдауна, нормализуем регистр
        if cleaned_line.startswith('#'):
            # Извлекаем текст после символов #
            match = re.match(r'(#+)\s*(.*)', cleaned_line)
            if match:
                hashes, content = match.groups()
                line = f"{hashes} {normalize_case(content)}\n"
        
        new_lines.append(line)
    
    # Записываем обратно, если что-то изменилось
    if skipped or True: # Применяем нормализацию в любом случае
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    return skipped

print("Запуск глобальной чистки всех памяток...")
count = 0
for filename in os.listdir(folder_path):
    if filename.endswith('.txt') or filename.endswith('.md'):
        if filename == 'тильда.md' or filename == 'gemini.md': continue
        filepath = os.path.join(folder_path, filename)
        if cleanup_file(filepath):
            print(f"[УДАЛЕНО] Лишняя строка в: {filename}")
        else:
            print(f"[ОК] Файл проверен: {filename}")
        count += 1

print(f"\nГотово! Обработано файлов: {count}")
