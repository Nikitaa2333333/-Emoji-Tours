import os
import re

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Регулярка для замены "Памятка: " на пустоту внутри атрибута value
    new_content = re.sub(r'value="Памятка:\s*', 'value="', content)

    if content != new_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Исправлено автозаполнение в: {file_path}")

def main():
    for filename in os.listdir("."):
        # Исправляем и сами файлы, и мастер-шаблон
        if (filename.startswith("memo-") or filename == "template_memo.html") and filename.endswith(".html"):
            process_file(filename)

if __name__ == "__main__":
    main()
