import pdfplumber
import os
import re

pdf_path = r"c:\Users\User\Downloads\tilda dododo\Памятка туриста  Египет.pdf"
output_path = r"c:\Users\User\Downloads\tilda dododo\egypt_extracted.txt"

def get_obj_top(obj, page_height):
    """Универсальное получение верхней координаты объекта в системе 'от верха'"""
    if 'top' in obj: return obj['top']
    if 'y1' in obj: return page_height - obj['y1']
    return None

def has_underline(page, line_words):
    if not line_words: return False
    
    h = page.height
    t_top = min(w['top'] for w in line_words)
    t_bottom = max(w['bottom'] for w in line_words)
    t_x0 = min(w['x0'] for w in line_words)
    t_x1 = max(w['x1'] for w in line_words)
    
    # Зона поиска линии: под текстом (от середины буквы до 8 пунктов ниже конца буквы)
    search_min_y = t_top + (t_bottom - t_top) / 2
    search_max_y = t_bottom + 8
    
    objs = page.lines + page.rects + page.curves
    
    for obj in objs:
        o_top = get_obj_top(obj, h)
        if o_top is None: continue
        
        # Если графический объект в вертикальной зоне текста
        if search_min_y <= o_top <= search_max_y:
            o_x0 = obj.get('x0', 0)
            o_x1 = obj.get('x1', 0)
            
            overlap_x0 = max(t_x0, o_x0)
            overlap_x1 = min(t_x1, o_x1)
            
            if overlap_x1 > overlap_x0:
                # Если линия покрывает более 30% ширины текста
                if (overlap_x1 - overlap_x0) / (t_x1 - t_x0) > 0.3:
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
                is_bold = any(k in fname_lower for k in ["bold", "heavy", "700", "800"])
                
                underlined = has_underline(page, line)
                current_top = line[0]['top']
                gap = current_top - last_bottom
                
                # Если это одна строка и она подчеркнута -> H3
                # Если просто жирная -> сохраняем <b>
                
                # 1. ЗАГОЛОВКИ H1/H2 (размер > 11.5)
                if is_bold and avg_size >= 11.5:
                    if current_block:
                         structure.append((f"{current_tag} " if current_tag else "") + " ".join(current_block))
                    current_tag = "[H1]" if not h1_found else "[H2]"
                    current_block = [raw_text]
                    h1_found = True
                
                # 2. ПОДЧЕРКНУТЫЙ ЗАГОЛОВОК H3
                elif is_bold and underlined:
                    if current_block:
                         structure.append((f"{current_tag} " if current_tag else "") + " ".join(current_block))
                    current_tag = "[H3]"
                    current_block = [raw_text]
                
                # 3. СПИСКИ
                elif raw_text.startswith(("-", "•", "—", "●")):
                    if current_block:
                         structure.append((f"{current_tag} " if current_tag else "") + " ".join(current_block))
                    current_tag = "[BULLET]"
                    current_block = [re.sub(r'^[\-•—●]\s*', '', raw_text)]
                
                # 4. ПРОДОЛЖЕНИЕ ТЕКСТА (очень близко к прошлой строке)
                elif gap < 12 and current_block and current_tag in [None, "[BULLET]"]:
                    current_block.append(f"<b>{raw_text}</b>" if is_bold else raw_text)
                
                # 5. НОВЫЙ БЛОК
                else:
                    if current_block:
                        structure.append((f"{current_tag} " if current_tag else "") + " ".join(current_block))
                    current_tag = None
                    current_block = [f"<b>{raw_text}</b>" if is_bold else raw_text]

                last_bottom = line[0]['bottom']

            if current_block:
                structure.append((f"{current_tag} " if current_tag else "") + " ".join(current_block))
            
            # Сброс для новой страницы
            last_bottom = 0

    return structure

print("Анализ графики PDF углублен. Мощный поиск подчеркиваний включен.")
content = extract_with_merging(pdf_path)
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(content))
