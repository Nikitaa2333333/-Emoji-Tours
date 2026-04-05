import os
import re

# Папки для исправления
target_dirs = [r'pages/memos', r'pages/countries']

# Паттерн для поиска черного фона при наведении
target_pattern = r'(\.nav-link:hover\s*{[^}]*background:\s*)rgb\(0,\s*0,\s*0\);'
# Новое значение (светлый прозрачный фон)
replacement = r'\1rgba(0, 0, 0, 0.04);'

files_fixed = 0

for target_dir in target_dirs:
    if not os.path.exists(target_dir):
        continue
    for filename in os.listdir(target_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(target_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'rgb(0, 0, 0)' in content:
                new_content = re.sub(target_pattern, replacement, content)
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"✅ Исправлено: {target_dir}/{filename}")
                    files_fixed += 1

print(f"\nГотово! Исправлено файлов: {files_fixed}")
