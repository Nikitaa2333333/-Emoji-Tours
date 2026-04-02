import pdfplumber
import os
import re

pdf_path = r"c:\Users\User\Downloads\tilda dododo\Памятка туриста  Египет.pdf"
output_path = r"c:\Users\User\Downloads\tilda dododo\egypt_extracted.txt"

BLACK_LIST = ["Приятного путешествия!", "2025 год"]
STOP_PHRASES = ["Краткий разговорник", "Фраза По-арабски Произношение"]

def get_obj_top(obj, page_height):
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
    search_min_y = t_top + (t_bottom - t_top) / 2
    search_max_y = t_bottom + 8
    objs = page.lines + page.rects + page.curves
    for obj in objs:
        o_top = get_obj_top(obj, h)
        if o_top is None: continue
        if search_min_y <= o_top <= search_max_y:
            o_x0 = obj.get('x0', 0); o_x1 = obj.get('x1', 0)
            overlap_x0 = max(t_x0, o_x0); overlap_x1 = min(t_x1, o_x1)
            if overlap_x1 > overlap_x0:
                if (overlap_x1 - overlap_x0) / (t_x1 - t_x0) > 0.3: return True
    return False

def find_column_divider(page):
    h = page.height
    v_lines = []
    objs = page.lines + page.rects
    for obj in objs:
        obj_top = get_obj_top(obj, h)
        obj_height = obj.get('height', abs(obj.get('bottom', 0) - obj.get('top', 0)))
        if obj_top < 100 or (obj_top + obj_height) > (h - 100): continue
        is_vertical = False
        if 'width' in obj and obj['width'] < 2 and obj_height > (h * 0.15):
            is_vertical, x = True, obj['x0']
        elif obj.get('x0') == obj.get('x1') and obj_height > (h * 0.15):
            is_vertical, x = True, obj['x0']
        if is_vertical and 250 < x < 350: v_lines.append(x)
    return max(set(v_lines), key=v_lines.count) if v_lines else None 

def extract_with_merging(pdf_path):
    structure, h1_found, stop_parsing = [], False, False
    is_embassy_section = False
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            if stop_parsing: break
            h = page.height
            divider_x = find_column_divider(page)
            words = page.extract_words(extra_attrs=["fontname", "size"])
            if not words: continue
            words.sort(key=lambda x: (x['top'], x['x0']))
            
            lines_data = []
            current_line = [words[0]]
            for i in range(1, len(words)):
                if abs(words[i]['top'] - words[i-1]['top']) < 3: current_line.append(words[i])
                else: lines_data.append(current_line); current_line = [words[i]]
            lines_data.append(current_line)

            current_block, current_tag, last_bottom = [], None, 0
            for line in lines_data:
                plain_text = " ".join([w['text'] for w in line]).strip()
                if not plain_text: continue
                if any(sp in plain_text for sp in STOP_PHRASES): stop_parsing = True; break
                if any(bl in plain_text for bl in BLACK_LIST): continue

                avg_size = sum([w['size'] for w in line]) / len(line)
                is_bold_first = any(k in line[0]['fontname'].lower() for k in ["bold", "heavy", "700", "800"])
                gap = line[0]['top'] - last_bottom
                underlined = has_underline(page, line)

                if is_bold_first and avg_size >= 11.5:
                    is_embassy_section = "полезная информация" in plain_text.lower()
                    if current_block: structure.append((f"{current_tag} " if current_tag else "") + " ".join(current_block))
                    current_tag = "[H1]" if not h1_found else "[H2]"; h1_found = True; current_block = [plain_text]
                elif is_embassy_section and divider_x:
                    tab_inserted = False
                    new_line = []
                    new_line.append(line[0])
                    for i in range(1, len(line)):
                        if line[i-1]['x1'] < divider_x and line[i]['x0'] > divider_x:
                            new_line.append({"text": "[TAB]"}); tab_inserted = True
                        new_line.append(line[i])
                    if line[0]['x0'] > divider_x + 10: new_line.insert(0, {"text": "[TAB]"}); tab_inserted = True
                    raw_parts = []
                    for w in new_line:
                        if w['text'] == "[TAB]": raw_parts.append("[TAB]")
                        else:
                            is_b = any(k in w['fontname'].lower() for k in ["bold", "heavy", "700", "800"])
                            raw_parts.append(f"<b>{w['text']}</b>" if is_b else w['text'])
                    raw_text = " ".join(raw_parts).replace(" [TAB] ", "[TAB]").replace("[TAB] ", "[TAB]").replace(" [TAB]", "[TAB]")
                    if tab_inserted:
                        if current_block: structure.append((f"{current_tag} " if current_tag else "") + " ".join(current_block))
                        current_tag, current_block = "[TABLE]", [raw_text]
                    else: current_block.append(raw_text)
                elif is_bold_first and underlined:
                    if current_block: structure.append((f"{current_tag} " if current_tag else "") + " ".join(current_block))
                    current_tag = "[H3]"; current_block = [plain_text]
                elif plain_text.startswith(("-", "•", "—", "●")):
                    if current_block: structure.append((f"{current_tag} " if current_tag else "") + " ".join(current_block))
                    current_tag = "[BULLET]"; current_block = [re.sub(r'^[\-•—●]\s*', '', plain_text)]
                elif gap < 12 and current_block and current_tag in [None, "[BULLET]"]:
                    current_block.append(f"<b>{plain_text}</b>" if is_bold_first else plain_text)
                else:
                    if current_block: structure.append((f"{current_tag} " if current_tag else "") + " ".join(current_block))
                    current_tag, current_block = (None, [f"<b>{plain_text}</b>" if is_bold_first else plain_text])
                last_bottom = line[0]['bottom']

            if current_block and not stop_parsing: structure.append((f"{current_tag} " if current_tag else "") + " ".join(current_block))
    return structure

print("Списки (буллиты) и подчеркивания (H3) восстановлены.")
content = extract_with_merging(pdf_path)
with open(output_path, "w", encoding="utf-8") as f: f.write("\n".join(content))
