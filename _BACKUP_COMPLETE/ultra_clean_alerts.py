import os
import re

def ultra_clean_alerts():
    directory = r'c:\Users\User\Downloads\tilda dododo'
    files = [f for f in os.listdir(directory) if f.startswith('memo-') and f.endswith('.html')]
    
    for filename in files:
        filepath = os.path.join(directory, filename)
        print(f"Ультра-очистка {filename}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Находим div-контейнеры плашек
        div_start = r'(<div\s+class="bg-\[#f5e2a1\]/5 border-l-8 border-primary p-10 rounded-r-\[3rem\] my-16 shadow-inner">)'
        parts = re.split(div_start, content)
        
        new_parts = [parts[0]]
        for i in range(1, len(parts), 2):
            trigger = parts[i]
            block_content = parts[i+1]
            
            # Конец блока
            end_div_idx = block_content.find('</div>\n                            </div>') # Finding the double closing or just end of block
            # Actually better to just look for the first </p> and its containing </div>
            
            # Находим область параграфа внутри блока
            p_pattern = re.compile(r'(<p[^>]*>)(.*?)(</p>)', re.DOTALL | re.IGNORECASE)
            
            def clean_final_text(match):
                p_open = match.group(1)
                text = match.group(2)
                p_close = match.group(3)
                
                # Убираем "Внимание!" (с любыми знаками препинания) из текста
                # И убираем лишние точки/пробелы, которые могли остаться
                text = re.sub(r'Внимание[!\.:]?\s*', '', text, flags=re.IGNORECASE)
                text = text.strip()
                
                # Если текст начинается с маленькой буквы после удаления, делаем большую
                if text:
                    text = text[0].upper() + text[1:]
                
                return f"{p_open}{text}{p_close}"

            block_content = p_pattern.sub(clean_final_text, block_content, count=1)
            new_parts.append(trigger + block_content)

        final_content = "".join(new_parts)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)
        print(f"  - Текст внутри плашек очищен от повторов.")

if __name__ == "__main__":
    ultra_clean_alerts()
