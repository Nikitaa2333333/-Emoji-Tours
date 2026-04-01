import os
import re

def clean_alerts():
    directory = r'c:\Users\User\Downloads\tilda dododo'
    files = [f for f in os.listdir(directory) if f.startswith('memo-') and f.endswith('.html')]
    
    # 1. Паттерн для поиска заголовка внутри плашки
    # Ищем span с классами заголовка внутри div плашки
    header_pattern = re.compile(
        r'(<div class="flex items-center gap-4 mb-6">.*?<span[^>]*>)(.*?)(</span>)',
        re.DOTALL | re.IGNORECASE
    )
    
    # 2. Паттерн для очистки текста в абзаце ниже
    # Ищем текст внутри <p>, который начинается с "на то, что" или содержит лишнее "Внимание!"
    text_pattern = re.compile(
        r'(<p[^>]*>)\s*(на то, что\s+)?(Внимание!\s+)?(.*?)(</p>)',
        re.DOTALL | re.IGNORECASE
    )

    for filename in files:
        filepath = os.path.join(directory, filename)
        print(f"Обработка {filename}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Заменяем все заголовки в плашках на "Внимание!"
        # Мы ищем блоки div с конкретными классами плашки
        blocks = re.split(r'(<div\s+class="bg-\[#f5e2a1\]/5 border-l-8 border-primary p-10 rounded-r-\[3rem\] my-16 shadow-inner">)', content)
        
        new_content_parts = [blocks[0]]
        for i in range(1, len(blocks), 2):
            trigger = blocks[i]
            block_content = blocks[i+1]
            
            # Конец блока
            end_div_idx = block_content.find('</div>')
            if end_div_idx == -1:
                new_content_parts.append(trigger + block_content)
                continue
                
            inner_content = block_content[:end_div_idx]
            rest_of_content = block_content[end_div_idx:]
            
            # 1. Правим заголовок
            inner_content = header_pattern.sub(r'\1Внимание!\3', inner_content)
            
            # 2. Правим текст абзаца
            def clean_p(match):
                p_open = match.group(1)
                main_text = match.group(4)
                p_close = match.group(5)
                # Капитализируем первую букву
                if main_text:
                    main_text = main_text[0].upper() + main_text[1:]
                return f"{p_open}{main_text}{p_close}"
            
            inner_content = text_pattern.sub(clean_p, inner_content)
            
            new_content_parts.append(trigger + inner_content + rest_of_content)

        final_content = "".join(new_content_parts)
        
        if final_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(final_content)
            print(f"  - Плашки успешно очищены.")
        else:
            print(f"  - Изменений не потребовалось.")

if __name__ == "__main__":
    clean_alerts()
