import os
import re

def update_html_files(root_dir):
    # Текст и ссылка по запросу пользователя
    privacy_url = "http://127.0.0.1:5500/privacy.html"
    consent_html_template = """
        <div class="flex items-center gap-3 px-1 mb-6">
          <input type="checkbox" id="privacy-consent" name="privacy-consent" required class="w-5 h-5 text-black border-black/20 rounded transition-colors cursor-pointer" />
          <label for="privacy-consent" class="text-sm font-medium text-black cursor-pointer">
            Согласен на <a href="{url}" target="_blank" class="underline hover:text-primary transition-colors">обработку персональных данных</a>
          </label>
        </div>"""

    for root, dirs, files in os.walk(root_dir):
        # Пропускаем папки с сырыми данными и библиотеки
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

            if 'privacy-consent' in content:
                print(f"Пропуск {file_path} - уже обновлен")
                continue

            # Ищем контейнер с кнопкой отправки
            # Паттерн учитывает разные варианты пробелов и переносов
            pattern = r'(<div class="pt-8 flex justify-center w-full">?\s*<button[^>]*type="submit"[^>]*>)'
            
            if re.search(pattern, content):
                print(f"Обновление {file_path}")
                consent_html = consent_html_template.format(url=privacy_url)
                new_content = re.sub(pattern, consent_html + r'\n\1', content)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                updated_count += 1
            else:
                # Попробуем найти просто кнопку submit, если контейнер другой
                pattern2 = r'(<button[^>]*type="submit"[^>]*>)'
                match = re.search(pattern2, content)
                if match:
                    # Но если это кнопка внутри формы, то вставляем перед ней
                    print(f"Обновление {file_path} (упрощенный поиск)")
                    consent_html = consent_html_template.format(url=privacy_url)
                    new_content = re.sub(pattern2, consent_html + r'\n\1', content)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    updated_count += 1
                else:
                    print(f"Форма не найдена в {file_path}")

        except Exception as e:
            print(f"Ошибка при обработке {file_path}: {e}")

    print(f"\nГотово! Обновлено файлов: {updated_count}")

if __name__ == "__main__":
    update_html_files(".")
