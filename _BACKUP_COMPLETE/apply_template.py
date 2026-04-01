import os
import re

def apply_template():
    template_path = 'template.html'
    if not os.path.exists(template_path):
        print(f"Error: {template_path} not found.")
        return

    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()

    html_files = [f for f in os.listdir('.') if f.endswith('.html') 
                  and f not in ['index.html', 'template.html'] 
                  and not f.startswith('memo-')]

    # Фразы для удаления
    kill_phrases = [
        "По всем вопросам свяжитесь",
        "E-mail: trohin.zh@yandex.ru",
        "Телефон: +7 (963) 649-18-52",
        "Соцсети: Вконтакте | Instagram | Telegram",
        "Индивидуальный предприниматель Трохин",
        "ИНН 503613656680",
        "ОГРН ИП 315507400016056"
    ]

    for filename in html_files:
        print(f"Processing {filename}...")
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Extract Country Name
        title_match = re.search(r'id="page-title"[^>]*>(.*?)</h1>', content, re.DOTALL)
        if title_match:
            country_name = title_match.group(1).strip()
        else:
            title_tag_match = re.search(r'<title>(.*?) — Emoji Tours</title>', content)
            if title_tag_match:
                country_name = title_tag_match.group(1).strip()
            else:
                country_name = filename.replace('.html', '').capitalize()

        # 2. Extract Hero Image
        hero_src = "placeholder_hero.jpg"
        hero_match = re.search(r'id="hero-image"[^>]*src="([^"]+)"', content)
        if hero_match and "placeholder" not in hero_match.group(1):
            hero_src = hero_match.group(1)
        else:
            all_imgs = re.findall(r'<img[^>]*src="([^"]+)"', content)
            for img in all_imgs:
                if any(x in img.lower() for x in ["logo", "icon", "placeholder", "google", "yandex"]):
                    continue
                hero_src = img
                break

        # 3. Extract Memo Content
        memo_area_match = re.search(r'id="memo-content-area"[^>]*>(.*?)</div>\s*<!-- ═══ ФОРМА', content, re.DOTALL)
        if not memo_area_match:
            memo_area_match = re.search(r'id="memo-content-area"[^>]*>(.*?)</div>\s*<section id="booking-form"', content, re.DOTALL)
        
        if memo_area_match:
            memo_html = memo_area_match.group(1).strip()
        else:
            fallback_match = re.search(r'</h1>(.*?)(?:<section id="booking-form"|<form)', content, re.DOTALL)
            memo_html = fallback_match.group(1).strip() if fallback_match else "<!-- No content found -->"

        # --- ОЧИСТКА ---
        # Удаляем параграфы, содержащие фразы из списка
        for phrase in kill_phrases:
            memo_html = re.sub(r'<p[^>]*>[^<]*' + re.escape(phrase) + r'[^<]*</p>', '', memo_html)
            # Также на всякий случай просто удаляем текст, если параграфы уже побились
            memo_html = memo_html.replace(phrase, "")

        # 4. Extract Slug
        memo_slug = filename.replace('.html', '')

        # 5. Extract H2s and Nav (always rebuild clean IDs)
        memo_html = re.sub(r'id="section-\d+"', '', memo_html)
        
        sections = re.findall(r'<h2[^>]*>(.*?)</h2>', memo_html)
        quick_links_html = ""
        modified_memo_html = memo_html
        
        for i, h2_text in enumerate(sections):
            section_id = f"section-{i}"
            clean_text = re.sub(r'<[^>]+>', '', h2_text).strip()
            quick_links_html += f'<a href="#{section_id}" class="nav-link">{clean_text}</a>\n'
            
            pattern = re.compile(r'<h2[^>]*>' + re.escape(h2_text) + r'</h2>')
            modified_memo_html = pattern.sub(f'<h2 id="{section_id}" class="text-6xl font-black mb-16 tracking-tight">{h2_text}</h2>', modified_memo_html, count=1)

        # Build final page
        new_page = template_content
        new_page = new_page.replace('██Название страны██', f"{country_name}")
        new_page = new_page.replace('██Название██', country_name)
        new_page = new_page.replace('██hero.jpg██', hero_src)
        new_page = new_page.replace('██slug██', memo_slug)
        new_page = new_page.replace('██Страна██', country_name)
        new_page = new_page.replace('<!-- Контент здесь -->', modified_memo_html)
        new_page = new_page.replace('<!-- Сюда вставим ссылки скриптом -->', quick_links_html)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_page)

    print("Successfully cleaned contact data from all pages.")

if __name__ == "__main__":
    apply_template()
