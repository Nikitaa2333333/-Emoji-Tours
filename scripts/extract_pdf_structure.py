import pdfplumber
import os
import re

pdf_path = r"c:\Users\User\Downloads\tilda dododo\Памятка туриста  Египет.pdf"
output_path = r"c:\Users\User\Downloads\tilda dododo\egypt_extracted.txt"

def has_underline(page, line_words):
    if not line_words: return False
    
    # Резюме координат текста
    text_top = min(w['top'] for w in line_words)
    text_bottom = max(w['bottom'] for w in line_words)
    text_x0 = min(w['x0'] for w in line_words)
    text_x1 = max(w['x1'] for w in line_words)
    
    # Собираем ВСЕ графические объекты
    # Проверяем все: lines, rects, curves
    objs = page.lines + page.rects + page.curves
    
    for obj in objs:
        # Иногда у объектов нет 'top'/'bottom', но есть 'y0'/'y1'
        y0 = obj.get('top', obj.get('y0'))
        y1 = obj.get('bottom', obj.get('y1'))
        x0 = obj.get('x0')
        x1 = obj.get('x1')
        
        if x0 is None or y0 is None: continue

        # Подчеркивание должно быть горизонтальным (высота < 4 пунктов)
        if abs(y0 - y1) > 4: continue
        
        # ПРОВЕРКА ПО ВЕРТИКАЛИ:
        # Линия может быть прямо на базовой линии текста или чуть ниже (до 6 пунктов)
        is_under_text = (text_bottom - 2 <= y0 <= text_bottom + 6)
        
        if is_under_text:
            # ПРОВЕРКА ПО ГОРИЗОНТАЛИ:
            # Линия должна пересекаться с текстом
            overlap_x0 = max(text_x0, x0)
            overlap_x1 = min(text_x1, x1)
            
            if overlap_x1 > overlap_x0:
                # Если линия перекрывает хотя бы 15% ширины текста - это оно!
                line_width = overlap_x1 - overlap_x0
                text_width = text_x1 - text_x0
                if line_width / text_width > 0.15:
                    return True
                
    return False

def extract_with_merging(pdf_path):
    structure = []
    h1_found = False
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words(extra_attrs=["fontname", "size"])
            if not words: continue

            lines_data = []
            current_line = [words[0]]
            for i in range(1, len(words)):
                if abs(words[i]['top'] - words[i-1]['top']) < 3:
                    current_line.append(words[i])
                else:
                    lines_data.append(current_line)
                    current_line = [words[i]]
            lines_data.append(current_line)

            current_block = []
            current_tag = None
            last_bottom = 0

            for line in lines_data:
                raw_text = " ".join([w['text'] for w in line]).strip()
                if not raw_text: continue
                
                avg_size = sum([w['size'] for w in line]) / len(line)
                fname_lower = line[0]['fontname'].lower()
                is_bold = any(k in fname_lower for k in ["bold", "heavy", "700", "800", "semibold"])
                
                current_top = line[0]['top']
                current_bottom = line[0]['bottom']
                underlined = has_underline(page, line)
                
                gap = current_top - last_bottom
                is_continuation = gap < 12 and last_bottom > 0

                # 1. СТРОГИЙ H1/H2 (Размер 12.0 по отчету)
                if is_bold and avg_size >= 11.8:
                    if current_block:
                         structure.append((f"{current_tag} " if current_tag else "") + " ".join(current_block))
                    current_tag = "[H1]" if not h1_found else "[H2]"
                    current_block = [raw_text]
                    h1_found = True
                    last_bottom = current_bottom
                
                # 2. ПОДЧЕРКНУТЫЙ H3 (Размер 9.0 + Линия)
                elif is_bold and underlined:
                    if current_block:
                         structure.append((f"{current_tag} " if current_tag else "") + " ".join(current_block))
                    current_tag = "[H3]"
                    current_block = [raw_text]
                    last_bottom = current_bottom
                
                # 3. СПИСКИ
                elif raw_text.startswith(("-", "•", "—", "●")):
                    if current_block:
                         structure.append((f"{current_tag} " if current_tag else "") + " ".join(current_block))
                    current_tag = "[BULLET]"
                    current_block = [re.sub(r'^[\-•—●]\s*', '', raw_text)]
                    last_bottom = current_bottom
                
                # 4. ОБЫЧНЫЙ ТЕКСТ (в том числе жирный без линий)
                else:
                    # Если это продолжение обычного текста
                    if is_continuation and current_block and current_tag not in ["[H1]", "[H2]", "[H3]", "[BULLET]"]:
                        # Если текст жирный внутри обычного блока — добавим разметку
                        if is_bold:
                            current_block.append(f"<b>{raw_text}</b>")
                        else:
                            current_block.append(raw_text)
                    else:
                        # Сбрасываем старый блок
                        if current_block:
                            structure.append((f"{current_tag} " if current_tag else "") + " ".join(current_block))
                        
                        current_tag = None 
                        if is_bold:
                            current_block = [f"<b>{raw_text}</b>"]
                        else:
                            current_block = [raw_text]
                    last_bottom = current_bottom

            if current_block:
                structure.append((f"{current_tag} " if current_tag else "") + " ".join(current_block))

    return structure

print(f"--- КАЛИБРОВАННЫЙ ПАРСИНГ (База: Times New Roman 12.0/9.0) ---")
content = extract_with_merging(pdf_path)
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(content))
print(f"Данные извлечены! Запускайте генерацию.")
