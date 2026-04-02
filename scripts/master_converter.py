import pdfplumber
import os
import re
import json
from bs4 import BeautifulSoup
import scripts.embassy_overrides as overrides

# Настройки путей
BASE_DIR = r"c:\Users\User\Downloads\tilda dododo"
TILDA_DIR = os.path.join(BASE_DIR, "tilda_raw", "emojitours.ru")
OUTPUT_DIR = os.path.join(BASE_DIR, "pages", "memos")
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "template_memo.html")

SLUG_MAP = {
    "Египет": "egypt", "Индонезия": "indonesia", "Китай": "china", "Маврикий": "mauritius",
    "Мальдивы": "maldives", "Сейшелы": "seychelles", "Тайланд": "thailand", "Танзания": "tanzania",
    "Тунис": "tunisia", "Турция": "turkey", "Шри-Ланка": "sri-lanka", "Вьетнам": "vietnam"
}

BLACK_LIST = ["Приятного путешествия!", "2025 год", "ПАМЯТКА ТУРИСТУ", "ПАМЯТКА ТУРИСТА"]
STOP_PHRASES = ["Краткий разговорник", "Фраза По-арабски Произношение"]

# --- МАППИНГ КАРТИНКИ ИЗ ТИЛЬДЫ ---
def get_tilda_content_map(country_name):
    """ Находит файл Тильды для страны и строит карту разделов с картинками """
    images_map = {}
    for filename in os.listdir(TILDA_DIR):
        if not filename.startswith("page") or not filename.endswith(".html"): continue
        path = os.path.join(TILDA_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            title = soup.find('title').text if soup.find('title') else ""
            if country_name.lower() in title.lower():
                # Нашли нужную страницу! Парсим секции
                recs = soup.find_all('div', class_='t-rec')
                last_header = None
                for r in recs:
                    txt_f = r.find('div', field='text')
                    if txt_f:
                        hdr = txt_f.find('strong')
                        if hdr and len(hdr.text.strip()) > 3: last_header = hdr.text.strip().lower()
                    
                    img = r.find('img', class_='t-img')
                    if img and last_header:
                        src = img.get('data-original') or img.get('src')
                        if src and "lib__icons" not in src:
                            images_map[last_header] = src
                return images_map
    return {}

def slugify_latin(text):
    trans_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
        'з': 'z', 'и': 'i', 'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
        'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
        'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }
    text = text.lower()
    for cyr, lat in trans_map.items(): text = text.replace(cyr, lat)
    text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    return text if text else "section"

def get_obj_top(obj, h): return obj['top'] if 'top' in obj else h - obj['y1']

def has_underline(page, line_words):
    if not line_words: return False
    h = page.height
    t_top = min(w['top'] for w in line_words)
    t_bottom = max(w['bottom'] for w in line_words)
    t_x0 = min(w['x0'] for w in line_words)
    t_x1 = max(w['x1'] for w in line_words)
    search_min_y, search_max_y = t_top + (t_bottom - t_top) / 2, t_bottom + 8
    for obj in (page.lines + page.rects + page.curves):
        o_top = get_obj_top(obj, h)
        if o_top and search_min_y <= o_top <= search_max_y:
            o_x0, o_x1 = obj.get('x0', 0), obj.get('x1', 0)
            overlap = min(t_x1, o_x1) - max(t_x0, o_x0)
            if overlap > 0 and overlap / (t_x1 - t_x0) > 0.4: return True
    return False

def find_column_divider(page):
    h, v_lines = page.height, []
    for obj in (page.lines + page.rects):
        top, height = get_obj_top(obj, h), obj.get('height', 0)
        if 80 < top < h - 80 and height > h * 0.1:
            if obj.get('width', 9) < 2 or obj.get('x0') == obj.get('x1'):
                if 200 < obj['x0'] < 400: v_lines.append(obj['x0'])
    return max(set(v_lines), key=v_lines.count) if v_lines else 300 

def extract_pdf(pdf_path):
    structure, h1_found, stop_parsing, is_embassy = [], False, False, False
    is_vietnam = "вьетнам" in pdf_path.lower()
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            if stop_parsing: break
            divider_x, words = find_column_divider(page), page.extract_words(extra_attrs=["fontname", "size"])
            if not words: continue
            words.sort(key=lambda x: (x['top'], x['x0']))
            lines, curr_l = [], [words[0]]
            for i in range(1, len(words)):
                if abs(words[i]['top'] - words[i-1]['top']) < 3: curr_l.append(words[i])
                else: lines.append(curr_l); curr_l = [words[i]]
            lines.append(curr_l)
            curr_b, curr_t, last_bot = [], None, 0
            for line in lines:
                plain = " ".join([w['text'] for w in line]).strip()
                if not plain or any(bl.lower() in plain.lower() for bl in BLACK_LIST): continue
                if any(sp in plain for sp in STOP_PHRASES): stop_parsing = True; break
                avg_s, is_bold = sum([w['size'] for w in line])/len(line), any(k in line[0]['fontname'].lower() for k in ["bold", "heavy", "700", "800"])
                gap = line[0]['top'] - last_bot if last_bot else 0
                if is_bold and avg_s >= 11.4:
                    is_embassy = any(k in plain.lower() for k in ["полезная информация", "посольства"])
                    if curr_b: structure.append(((curr_t + " ") if curr_t else "") + " ".join(curr_b))
                    curr_t, curr_b, h1_found = ("[H1]" if not h1_found else "[H2]"), [plain], True
                elif is_embassy and divider_x:
                    tab_in, raw_p = False, []
                    for i, w in enumerate(line):
                        if i > 0 and line[i-1]['x1'] < divider_x < w['x0']: raw_p.append("[TAB]"); tab_in = True
                        raw_p.append(f"<b>{w['text']}</b>" if any(k in w.get('fontname','').lower() for k in ["bold","heavy","700"]) else w['text'])
                    if line[0]['x0'] > divider_x + 10: raw_p.insert(0, "[TAB]"); tab_in = True
                    raw_text = " ".join(raw_p).replace(" [TAB] ", "[TAB]").replace("[TAB] ", "[TAB]")
                    if tab_in:
                        if curr_b: structure.append(((curr_t + " ") if curr_t else "") + " ".join(curr_b))
                        curr_t, curr_b = "[TABLE]", [raw_text]
                    else: curr_b.append(raw_text)
                elif is_bold and (has_underline(page, line) or (is_vietnam and avg_s > 9.5 and gap > 15)):
                    if curr_b: structure.append(((curr_t+ " ") if curr_t else "") + " ".join(curr_b))
                    curr_t, curr_b = "[H3]", [plain]
                elif plain.startswith(("-", "•", "—", "●")):
                    if curr_b: structure.append(((curr_t+ " ") if curr_t else "") + " ".join(curr_b))
                    curr_t, curr_b = "[BULLET]", [re.sub(r'^[\-•—●]\s*', '', plain)]
                elif gap < 5 and curr_b and curr_t not in ["[H1]", "[H2]", "[H3]"]: curr_b.append(f"<b>{plain}</b>" if is_bold else plain)
                else: 
                    if curr_b: structure.append(((curr_t+ " ") if curr_t else "") + " ".join(curr_b))
                    curr_t, curr_b = None, [f"<b>{plain}</b>" if is_bold else plain]
                last_bot = line[0]['bottom']
            if curr_b and not stop_parsing: structure.append(((curr_t + " ") if curr_t else "") + " ".join(curr_b))
    return structure

def render_html(lines, country_name, slug):
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f: template = f.read()
    # Загружаем карту картинок из Тильды
    tilda_images = get_tilda_content_map(country_name)
    main_c, nav_l, in_list, table_buf = "", "", False, []

    def flush_table():
        nonlocal main_c, table_buf
        if not table_buf: return
        if slug in overrides.EMBASSY_OVERRIDES:
            main_c += '<div class="space-y-12 my-10">\n'
            for item in overrides.EMBASSY_OVERRIDES[slug]:
                main_c += f'  <div><h3 class="text-2xl font-black mb-4 text-black">{item["name"]}</h3>'
                main_c += f'<p class="text-lg text-black/80 font-manrope">{item["body"].replace("\n","<br>")}</p></div>\n'
            main_c += '</div>\n'; table_buf = []
            return
        c1, c2 = [], []
        for lb in table_buf:
            pts = lb.replace("[TABLE]", "").strip().split("[TAB]")
            c1.append(pts[0] if len(pts)>0 else ""); c2.append(pts[1] if len(pts)>1 else "")
        main_c += '<div class="space-y-12 my-10">\n'
        for col in [c1, c2]:
            cl = [p for p in col if p.strip()]
            if not cl: continue
            hdr = re.sub(r'</?b>', '', cl[0]).strip()
            bdy = "<br>\n".join([p.replace("<b>",'<span class="font-bold text-black">').replace("</b>",'</span>') for p in cl[1:]])
            main_c += f'  <div><h3 class="text-2xl font-black mb-4 text-black">{hdr}</h3><p class="text-lg text-black/80 font-manrope">{bdy}</p></div>\n'
        main_c += '</div>\n'; table_buf = []

    for line in lines:
        line = line.strip()
        if not line: continue
        if not line.startswith("[TABLE]") and table_buf: flush_table()
        line = re.sub(r'<b>(.*?)</b>', r'<span class="font-bold text-black">\1</span>', line)
        
        if line.startswith("[H2]"):
            if in_list: main_c += "</ul>\n"; in_list = False
            txt = line.replace("[H2]", "").strip(); slg = slugify_latin(txt)
            main_c += f'<section id="{slg}" class="scroll-mt-32 mb-20">\n<h2 class="text-3xl md:text-5xl font-black mb-10 tracking-tight text-black">{txt}</h2>\n'
            # ВСТАВКА КАРТИНКИ
            img_url = tilda_images.get(txt.lower())
            if img_url:
                main_c += f'<div class="mb-10 overflow-hidden rounded-3xl shadow-2xl"><img src="../../tilda_raw/emojitours.ru/{img_url}" class="w-full h-auto"></div>\n'
            nav_l += f'<a href="#{slg}" class="nav-link">{txt}</a>\n'
        elif line.startswith("[H3]"):
            if in_list: main_c += "</ul>\n"; in_list = False
            txt = line.replace("[H3]", "").strip()
            main_c += f'<h3 class="text-2xl font-bold mt-12 mb-6 underline decoration-primary underline-offset-8 text-black">{txt}</h3>\n'
        elif line.startswith("[BULLET]"):
            if not in_list: main_c += '<ul class="check-list mb-8">\n'; in_list = True
            main_c += f'<li>{line.replace("[BULLET]", "").strip()}</li>\n'
        elif line.startswith("[TABLE]"): table_buf.append(line)
        elif not line.startswith("[H1]"):
            if in_list: main_c += "</ul>\n"; in_list = False
            main_c += f'<p class="mb-6 text-xl text-black/80 leading-relaxed font-manrope">{line}</p>\n'
            
    flush_table()
    if in_list: main_c += "</ul>\n"
    return template.replace("██Название страны██", country_name).replace("██Название██", country_name).replace("██slug██", slug).replace("<!-- Контент -->", main_c).replace("<!-- Ссылки -->", nav_l)

def main():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    for pdf_file in [f for f in os.listdir(BASE_DIR) if f.startswith("Памятка туриста") and f.endswith(".pdf")]:
        c_name = re.sub(r'Памятка туриста\s+', '', pdf_file).replace('.pdf', '').strip()
        slug = SLUG_MAP.get(c_name, "memo")
        print(f"--- Обработка: {c_name} ---")
        try:
            html = render_html(extract_pdf(os.path.join(BASE_DIR, pdf_file)), c_name, slug)
            with open(os.path.join(OUTPUT_DIR, f"{slug}.html"), "w", encoding="utf-8") as f: f.write(html)
            print(f"Успех: {slug}.html")
        except: import traceback; traceback.print_exc()

if __name__ == "__main__": main()
