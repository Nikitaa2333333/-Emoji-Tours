import re
import os

def build_final_memo_perfect_lines(tilda_file, template_file, output_file):
    print(f"--- УСТРАНЕНИЕ РАЗРЫВОВ ТЕКСТА ---")
    
    with open(tilda_file, 'r', encoding='utf-8') as f:
        tilda_html = f.read()
    with open(template_file, 'r', encoding='utf-8') as f:
        template = f.read()

    # 1. СТРУКТУРА МЕНЮ
    nav_items = re.findall(r'href="(#(?:submenu:|rec)[^"]+)"[^>]*>(.*?)</a>', tilda_html)
    total_structure = []
    id_to_title = {}

    for href, title in nav_items:
        clean_cat = re.sub(r'<[^>]*>', '', title).strip()
        if not clean_cat or len(clean_cat) < 2: continue
        subs = []
        if 'submenu:' in href:
            pattern = fr'data-tooltip-hook="{href}"(.*?)</ul'
            sub_match = re.search(pattern, tilda_html, re.DOTALL)
            if sub_match:
                sub_links = re.findall(r'href="(#[^"]+)"[^>]*>(.*?)</a>', sub_match.group(1))
                for s_id, s_title in sub_links:
                    sid = s_id.replace('#', '')
                    stitle = re.sub(r'<[^>]*>', '', s_title).strip()
                    subs.append({'id': sid, 'title': stitle})
                    id_to_title[sid] = stitle
        elif href.startswith('#rec'):
            sid = href.replace('#', '')
            subs.append({'id': sid, 'title': clean_cat})
            id_to_title[sid] = clean_cat
        total_structure.append({'main': clean_cat, 'subs': subs})

    # 2. КОНТЕНТ С УМНОЙ СКЛЕЙКОЙ
    parts = re.split(r'<a name="[^"]+"', tilda_html)
    names = re.findall(r'<a name="([^"]+)"', tilda_html)
    content_html = ""
    
    for i, name in enumerate(names):
        if name in id_to_title:
            raw_content = parts[i+1]
            clean_body = re.sub(r'<style>.*?</style>|<script>.*?</script>', '', raw_content, flags=re.DOTALL)
            # Очищаем все теги, оставляя структуру строк
            text_only = re.sub(r'<[^>]*>', '\n', clean_body, flags=re.DOTALL)
            
            img_match = re.search(r'data-original="([^"]+)"', raw_content)
            img_tag = f'<img src="{img_match.group(1)}" class="w-full h-auto rounded-[3.5rem] shadow-xl mb-12" alt="{id_to_title[name]}">' if img_match else ""

            # УМНАЯ СКЛЕЙКА СТРОК
            # 1. Заменяем одиночные переносы строк на пробелы, но сохраняем двойные (как пустые строки)
            # И сохраняем переносы перед буллитами
            lines = text_only.split('\n')
            paragraphs = []
            buffer = []
            
            for line in lines:
                line = line.strip()
                if not line or 'style=' in line:
                    if buffer:
                        paragraphs.append(" ".join(buffer))
                        buffer = []
                    continue
                
                # Если это начало списка
                if line.startswith('●') or line.startswith('•'):
                    if buffer:
                        paragraphs.append(" ".join(buffer))
                        buffer = []
                    paragraphs.append(line) # Список сохраняем отдельной строкой
                else:
                    # Склеиваем с предыдущей строкой
                    buffer.append(line)
            
            if buffer: paragraphs.append(" ".join(buffer))

            # ФОРМИРОВАНИЕ HTML
            formatted_elements = []
            current_list = []
            
            for p in paragraphs:
                if p.startswith('●') or p.startswith('•'):
                    current_list.append(p.strip('●• ').strip())
                else:
                    if current_list:
                        items = "".join([f'<li>{it}</li>' for it in current_list if len(it)>2])
                        formatted_elements.append(f'<ul class="check-list mb-10">{items}</ul>')
                        current_list = []
                    if len(p) > 10:
                        formatted_elements.append(f'<p class="mb-6">{p}</p>')
            
            if current_list:
                items = "".join([f'<li>{it}</li>' for it in current_list if len(it)>2])
                formatted_elements.append(f'<ul class="check-list mb-10">{items}</ul>')

            content_html += f'''
            <section id="{name}" class="scroll-mt-32 mb-28">
                <h2 class="text-5xl font-black mb-12 tracking-tight leading-none text-black">{id_to_title[name]}</h2>
                {img_tag}
                <div class="text-on-surface-variant font-medium text-xl leading-relaxed max-w-4xl">
                    {"".join(formatted_elements)}
                </div>
                <div class="h-px bg-black/[0.05] mt-20"></div>
            </section>'''

    # Остальная часть (меню и сборка) совпадает
    menu_html = ""
    for cat in total_structure:
        if not cat['subs']: continue
        menu_html += f'<div class="py-6 border-b border-black/[0.05]">'
        menu_html += f'<p class="px-6 text-[10px] font-black uppercase tracking-[0.4em] text-black/20 mb-4">{cat["main"]}</p>'
        for sub in cat['subs']:
            menu_html += f'<a href="#{sub["id"]}" class="nav-link !text-xs !py-1.5">{sub["title"]}</a>'
        menu_html += f'</div>'

    final_output = template.replace('██Название страны██', 'Египет').replace('██Название██', 'Египет').replace('██slug██', 'egypt')
    final_output = final_output.replace('<!-- Ссылки -->', menu_html).replace('<!-- Мобильные ссылки -->', menu_html).replace('<!-- Контент -->', content_html)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_output)
    print(f"--- УСПЕХ: Текст склеен и выглядит монолитно! ---")

if __name__ == "__main__":
    build_final_memo_perfect_lines('content/тильда.txt', 'templates/template_memo.html', 'labs/egypt_final.html')
