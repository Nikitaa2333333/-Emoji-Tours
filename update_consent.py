import os
import re

def get_relative_privacy_path(file_path, root_dir):
    """Calculates relative path from file_path to privacy.html in root_dir."""
    abs_file_dir = os.path.dirname(os.path.abspath(file_path))
    abs_root_dir = os.path.abspath(root_dir)
    
    # Count how many steps up to root
    rel_path = os.path.relpath(abs_root_dir, abs_file_dir)
    if rel_path == '.':
        return 'privacy.html'
    return os.path.join(rel_path, 'privacy.html').replace('\\', '/')

def update_html_files(root_dir):
    targets = []
    for root, dirs, files in os.walk(root_dir):
        if any(d in root.lower() for d in ['.git', '.venv', 'tilda_raw', 'images', 'css']):
            continue
        for file in files:
            if file.endswith('.html'):
                targets.append(os.path.join(root, file))

    updated_count = 0
    for file_path in targets:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            privacy_rel_path = get_relative_privacy_path(file_path, root_dir)
            
            consent_html = f"""
        <div class="flex items-center gap-3 px-1 mb-6">
          <input type="checkbox" id="privacy-consent" name="privacy-consent" required class="w-5 h-5 text-black border-black/20 rounded transition-colors cursor-pointer" />
          <label for="privacy-consent" class="text-sm font-medium text-black cursor-pointer">
            Согласен на <a href="{privacy_rel_path}" target="_blank" class="!text-black !underline underline-offset-4 decoration-black/40 hover:decoration-black transition-all">обработку персональных данных</a>
          </label>
        </div>"""

            # Паттерн для поиска любого блока с id="privacy-consent" (даже если ссылка абсолютная или другая)
            # Мы ищем div, внутри которого есть наш checkbox-id
            pattern = re.compile(r'<div class="flex items-center gap-3 px-1 mb-6">.*?id="privacy-consent".*?</div>', re.DOTALL)
            
            if pattern.search(content):
                new_content = pattern.sub(consent_html.strip(), content)
                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    updated_count += 1
                continue

            # На случай файлов без блока (добавление перед кнопкой отправки)
            btn_pattern = r'(<button[^>]*type="submit"[^>]*>)'
            if re.search(btn_pattern, content):
                new_content = re.sub(btn_pattern, consent_html.strip() + r'\n\1', content)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                updated_count += 1

        except Exception as e:
            print(f"Ошибка {file_path}: {e}")

    print(f"\nГотово! Относительные ссылки на политику конфиденциальности обновлены в {updated_count} файлах.")

if __name__ == "__main__":
    update_html_files(".")
