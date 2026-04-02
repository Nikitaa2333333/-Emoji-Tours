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

def generate_html():
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    main_content = ""
    nav_links = ""
    in_list = False
    
    for line in lines:
        line = line.strip()
        if not line: continue

        # Обработка жирности в тексте (замена <b> на span с жирностью для чистоты)
        line = re.sub(r'<b>(.*?)</b>', r'<span class="font-bold text-black">\1</span>', line)

        if line.startswith("[H2]"):
            if in_list:
                main_content += "</ul>\n"
                in_list = False
            text = line.replace("[H2]", "").strip()
            slug = slugify(text)
            main_content += f'<section id="{slug}" class="scroll-mt-32">\n'
            main_content += f'  <h2 class="text-3xl md:text-5xl font-black mb-8 tracking-tight">{text}</h2>\n'
            nav_links += f'<a href="#{slug}" class="nav-link">{text}</a>\n'
        
        elif line.startswith("[H3]"):
            if in_list:
                main_content += "</ul>\n"
                in_list = False
            text = line.replace("[H3]", "").strip()
            main_content += f'<h3 class="text-xl font-bold mt-10 mb-6 underline decoration-primary underline-offset-8">{text}</h3>\n'
        
        elif line.startswith("[BULLET]"):
            if not in_list:
                main_content += '<ul class="check-list">\n'
                in_list = True
            text = line.replace("[BULLET]", "").strip()
            main_content += f'  <li>{text}</li>\n'
        
        elif line.startswith("[H1]"):
            # Пропускаем H1, так как он идет в заголовок страницы ██Название██
            continue
            
        else:
            if in_list:
                main_content += "</ul>\n"
                in_list = False
            main_content += f'<p class="mb-6 py-1 text-lg text-black/80 leading-relaxed">{line}</p>\n'

        if line.startswith("[H2]") and "</section>" not in main_content:
            # Это логическое закрытие секции будет добавлено при следующем H2 или в конце
            pass

    if in_list:
        main_content += "</ul>\n"

    # Финальная сборка с учетом меток в шаблоне
    final_html = template
    final_html = final_html.replace("██Название страны██", "Египет")
    final_html = final_html.replace("██Название██", "Египет")
    final_html = final_html.replace("██slug██", "egypt")
    final_html = final_html.replace("<!-- Контент -->", main_content)
    final_html = final_html.replace("<!-- Ссылки -->", nav_links)
    
    # Резервные метки на всякий случай
    final_html = final_html.replace("<!-- MAIN_CONTENT -->", main_content)
    final_html = final_html.replace("<!-- NAV_LINKS -->", nav_links)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_html)
    
    print("Success! HTML восстановлен и синхронизирован с шаблоном.")

if __name__ == "__main__":
    generate_html()
