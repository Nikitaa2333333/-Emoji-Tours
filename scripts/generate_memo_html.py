import os
import re

input_file = r"c:\Users\User\Downloads\tilda dododo\egypt_extracted.txt"
output_file = r"c:\Users\User\Downloads\tilda dododo\pages\memos\egypt_new.html"
template_path = r"c:\Users\User\Downloads\tilda dododo\templates\template_memo.html"

def slugify(text):
    text = text.lower()
    chars = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'yo','ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h','ц':'ts','ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya'}
    res = []
    for char in text:
        if char in chars: res.append(chars[char])
        elif char.isalnum(): res.append(char)
        else: res.append('-')
    return re.sub(r'-+', '-', "".join(res)).strip('-')

def render_table_block(table_lines):
    col1_content, col2_content = [], []
    for line in table_lines:
        parts = line.replace("[TABLE]", "").strip().split("[TAB]")
        col1_content.append(parts[0] if len(parts) > 0 else "")
        col2_content.append(parts[1] if len(parts) > 1 else "")

    html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-8 my-10">\n'
    for col in [col1_content, col2_content]:
        clean_col = [p for p in col if p.strip()]
        if not clean_col: continue
        header = re.sub(r'</?b>', '', clean_col[0])
        body = "<br>".join(clean_col[1:])
        body = body.replace("<b>", '<span class="font-bold text-black">').replace("</b>", '</span>')
        html += f'  <div class="bg-gray-50/50 p-8 rounded-2xl border border-gray-100 shadow-sm h-full">\n'
        html += f'    <div class="text-xl font-bold mb-4 text-black">{header}</div>\n'
        html += f'    <div class="text-lg text-black/70 leading-relaxed">{body}</div>\n'
        html += f'  </div>\n'
    html += '</div>\n'
    return html

def generate_html():
    if not os.path.exists(input_file): return
    with open(input_file, "r", encoding="utf-8") as f: lines = f.readlines()
    with open(template_path, "r", encoding="utf-8") as f: template = f.read()

    main_content, nav_links = "", ""
    in_list, table_buffer = False, []

    def flush_table():
        nonlocal main_content, table_buffer
        if table_buffer:
            main_content += render_table_block(table_buffer)
            table_buffer = []

    for line in lines:
        line = line.strip()
        if not line: continue
        if not line.startswith("[TABLE]") and table_buffer: flush_table()
        
        line = re.sub(r'<b>(.*?)</b>', r'<span class="font-bold text-black">\1</span>', line)

        if line.startswith("[H2]"):
            if in_list: main_content += "</ul>\n"; in_list = False
            text = line.replace("[H2]", "").strip()
            slug = slugify(text)
            main_content += f'<section id="{slug}" class="scroll-mt-32">\n'
            main_content += f'  <h2 class="text-3xl md:text-5xl font-black mb-8 tracking-tight">{text}</h2>\n'
            nav_links += f'<a href="#{slug}" class="nav-link">{text}</a>\n'
        elif line.startswith("[H3]"):
            if in_list: main_content += "</ul>\n"; in_list = False
            text = line.replace("[H3]", "").strip()
            main_content += f'<h3 class="text-xl font-bold mt-10 mb-6 underline decoration-primary underline-offset-8">{text}</h3>\n'
        elif line.startswith("[BULLET]"):
            if not in_list: main_content += '<ul class="check-list">\n'; in_list = True
            main_content += f'  <li>{line.replace("[BULLET]", "").strip()}</li>\n'
        elif line.startswith("[TABLE]"):
            if in_list: main_content += "</ul>\n"; in_list = False
            table_buffer.append(line)
        elif line.startswith("[H1]"): continue
        else:
            if in_list: main_content += "</ul>\n"; in_list = False
            main_content += f'<p class="mb-6 py-1 text-lg text-black/80 leading-relaxed font-manrope">{line}</p>\n'

    flush_table()
    if in_list: main_content += "</ul>\n"

    final_html = template.replace("██Название страны██", "Египет").replace("██Название██", "Египет").replace("██slug██", "egypt")
    final_html = final_html.replace("<!-- Контент -->", main_content).replace("<!-- Ссылки -->", nav_links)
    final_html = final_html.replace("<!-- MAIN_CONTENT -->", main_content).replace("<!-- NAV_LINKS -->", nav_links)

    with open(output_file, "w", encoding="utf-8") as f: f.write(final_html)
    print("Success! Посольства возвращены, остальное не тронуто.")

if __name__ == "__main__":
    generate_html()
