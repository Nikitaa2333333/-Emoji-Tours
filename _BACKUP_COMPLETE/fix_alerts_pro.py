import os
import re

def fix_alerts():
    directory = r'c:\Users\User\Downloads\tilda dododo'
    files = [f for f in os.listdir(directory) if f.startswith('memo-') and f.endswith('.html')]
    
    # 1. Исправляем иконку (если она была заменена на "Внимание!")
    icon_cleanup = re.compile(
        r'(<span[^>]*class="material-symbols-outlined[^>]*">)Внимание!(</span>)',
        re.IGNORECASE
    )
    
    # 2. Исправляем заголовок (второй span в блоке)
    # Ищем блок целиком, чтобы точно заменить второй span
    block_pattern = re.compile(
        r'(<div class="flex items-center gap-4 mb-6">.*?<span[^>]*class="material-symbols-outlined[^>]*">.*?</span>.*?</div>\s*<span[^>]*>)(.*?)(</span>)',
        re.DOTALL | re.IGNORECASE
    )

    # 3. Очищаем текст абзаца
    paragraph_pattern = re.compile(
        r'(<p[^>]*>)\s*(на то, что\s+|Внимание!\s+)*(.*?)(</p>)',
        re.DOTALL | re.IGNORECASE
    )

    for filename in files:
        filepath = os.path.join(directory, filename)
        print(f"Исправление {filename}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Шаг 1: Возвращаем иконку (ставим priority_high как универсальный вариант)
        content = icon_cleanup.sub(r'\1priority_high\2', content)
        
        # Шаг 2: Ищем все плашки и унифицируем
        # Находим div-контейнер плашки
        div_start = r'<div\s+class="bg-\[#f5e2a1\]/5 border-l-8 border-primary p-10 rounded-r-\[3rem\] my-16 shadow-inner">'
        parts = re.split(f'({div_start})', content)
        
        new_parts = [parts[0]]
        for i in range(1, len(parts), 2):
            trigger = parts[i]
            block_content = parts[i+1]
            
            # Находим заголовок (второй span)
            # В структуре два span: первый с иконкой, второй с текстом.
            # Мы заменим текст во втором span.
            def replace_label(match):
                # match.group(2) - это текущий текст заголовка
                return match.group(1) + "Внимание!" + match.group(3)

            # Ищем span, который идет ПОСЛЕ закрывающего div с иконкой
            block_content = re.sub(
                r'(</div>\s*<span[^>]*>)(.*?)(</span>)',
                r'\1Внимание!\3',
                block_content,
                count=1,
                flags=re.DOTALL | re.IGNORECASE
            )
            
            # Шаг 3: Чистим параграф
            def clean_paragraph(match):
                p_open = match.group(1)
                main_text = match.group(3).strip()
                p_close = match.group(4)
                if main_text:
                    main_text = main_text[0].upper() + main_text[1:]
                return f"{p_open}{main_text}{p_close}"

            block_content = paragraph_pattern.sub(clean_paragraph, block_content, count=1)
            
            new_parts.append(trigger + block_content)

        final_content = "".join(new_parts)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)
        print(f"  - Файл восстановлен и очищен.")

if __name__ == "__main__":
    fix_alerts()
