import re
import os

def slugify(text):
    text = text.lower()
    chars = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'yo','ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h','ц':'ts','ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya',' ':'-', '.':''}
    for char, replacement in chars.items(): text = text.replace(char, replacement)
    return re.sub(r'[^a-z0-9-]', '', text).strip('-')

def generate_html():
    with open('egypt_extracted.txt', 'r', encoding='utf-8') as f: content_lines = f.readlines()
    with open('templates/template_memo.html', 'r', encoding='utf-8') as f: template = f.read()

    sections = []
    current_section = None
    
    for line in content_lines:
        line = line.strip()
        if not line: continue
        if line.startswith('[H1]') or line.startswith('[H2]'):
            title = line[4:].strip()
            current_section = {'title': title, 'slug': slugify(title), 'content': []}
            sections.append(current_section)
        elif current_section:
            if line.startswith('[H3]'):
                current_section['content'].append(('h3', line[4:].strip()))
            elif line.startswith('[BULLET]'):
                current_section['content'].append(('bullet', line[8:].strip()))
            else:
                current_section['content'].append(('paragraph', line))

    main_content = ""
    sidebar = []
    for s in sections:
        sidebar.append(f'<a href="#{s["slug"]}" class="nav-link">{s["title"]}</a>')
        main_content += f'<section id="{s["slug"]}" class="scroll-mt-32 "><h2 class="text-3xl md:text-5xl font-black mb-8">{s["title"]}</h2>'
        in_list = False
        for type, text in s['content']:
            if type == 'h3':
                if in_list: main_content += '</ul>'; in_list = False
                main_content += f'<h3 class="text-xl font-bold mt-8 mb-4 underline decoration-primary underline-offset-4">{text}</h3>'
            elif type == 'bullet':
                if not in_list: main_content += '<ul class="check-list">'; in_list = True
                main_content += f'<li>{text}</li>'
            else:
                if in_list: main_content += '</ul>'; in_list = False
                # Заменяем ** на теги жирного шрифта</b>
                clean_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                main_content += f'<p class="mb-4 text-lg text-black/80">{clean_text}</p>'
        if in_list: main_content += '</ul>'
        main_content += '</section>'

    final = template.replace('██Название страны██', 'Египет').replace('██Название██', 'Египет').replace('██slug██', 'egypt')
    final = final.replace('<!-- Ссылки -->', "\n".join(sidebar)).replace('<!-- Контент -->', main_content)
    with open('pages/memos/egypt_new.html', 'w', encoding='utf-8') as f: f.write(final)
    print("Success! HTML updated with Bold support and H3.")

generate_html()
