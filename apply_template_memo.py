import os
import re

def apply_template_memo():
    template_path = 'template_memo.html'
    if not os.path.exists(template_path):
        print(f"Error: {template_path} not found.")
        return

    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()

    # Get all memo files
    memo_files = [f for f in os.listdir('.') if f.startswith('memo-') and f.endswith('.html')]

    # Phrases to kill (same as main pages)
    kill_phrases = [
        "По всем вопросам свяжитесь",
        "E-mail: trohin.zh@yandex.ru",
        "Телефон: +7 (963) 649-18-52",
        "Соцсети: Вконтакте | Instagram | Telegram",
        "Индивидуальный предприниматель Трохин",
        "ИНН 503613656680",
        "ОГРН ИП 315507400016056"
    ]

    for filename in memo_files:
        print(f"Processing {filename}...")
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Extract Country Name from Title
        # Title usually like "Памятка: Египет — Emoji Tours"
        title_match = re.search(r'<title>Памятка:\s*(.*?)\s*— Emoji Tours</title>', content)
        if title_match:
            country_name = title_match.group(1).strip()
        else:
            # Fallback to h1 or filename
            h1_match = re.search(r'id="page-title"[^>]*>Памятка:\s*(.*?)</h1>', content)
            if h1_match:
                country_name = h1_match.group(1).strip()
            else:
                country_name = filename.replace('memo-', '').replace('.html', '').capitalize()

        # 2. Extract Memo Content
        memo_area_match = re.search(r'id="memo-content-area"[^>]*>(.*?)</div>\s*<!-- ═══ ФОРМА', content, re.DOTALL)
        if not memo_area_match:
             memo_area_match = re.search(r'id="memo-content-area"[^>]*>(.*?)</div>\s*<section id="booking-form"', content, re.DOTALL)
        
        if memo_area_match:
            memo_html = memo_area_match.group(1).strip()
        else:
            # If area is missing, we take everything between main title and form
            fallback_match = re.search(r'</h1>(.*?)(?:<section id="booking-form"|<form)', content, re.DOTALL)
            memo_html = fallback_match.group(1).strip() if fallback_match else "<!-- No content found -->"

        # --- ОЧИСТКА ---
        for phrase in kill_phrases:
            memo_html = re.sub(r'<p[^>]*>[^<]*' + re.escape(phrase) + r'[^<]*</p>', '', memo_html)
            memo_html = memo_html.replace(phrase, "")

        # 3. Clean up H2s (remove IDs if already present)
        memo_html = re.sub(r'id="section-\d+"', '', memo_html)
        
        # 4. Generate Nav Links and Clean Content
        # We find sections and process them
        # Section pattern: <section class="pt-24 border-t border-black/5"> ... </section>
        section_regex = re.compile(r'<section class="pt-24 border-t border-black/5">(.*?)</section>', re.DOTALL)
        sections_found = section_regex.findall(memo_html)
        
        quick_links_html = ""
        cleaned_memo_html = ""
        
        section_idx = 0
        for section_inner in sections_found:
            h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', section_inner, re.DOTALL)
            if not h2_match:
                continue
                
            h2_text = h2_match.group(1).strip()
            clean_text = re.sub(r'<[^>]+>', '', h2_text).strip()
            
            # --- HANDLE PHOTOS ---
            photo_match = re.search(r'Фото:\s*(tild[a-zA-Z0-9_\-\.]+\.(?:jpg|png|webp|jpeg|gif))', section_inner, re.IGNORECASE)
            if photo_match:
                photo_file = photo_match.group(1).strip()
                if os.path.exists(photo_file):
                    img_tag = f'<img src="{photo_file}" class="w-full h-[500px] object-cover rounded-[3rem] shadow-xl mb-12" loading="lazy">'
                    # Replace the "Фото: ..." text wherever it is with the img tag
                    section_inner = re.sub(r'Фото:\s*tild[a-zA-Z0-9_\-\.]+\.(?:jpg|png|webp|jpeg|gif)', img_tag, section_inner, flags=re.IGNORECASE)
                    
                    # If the h2 text was JUST the photo link, we clear common text
                    current_h2_clean = re.sub(r'<[^>]+>', '', h2_text).strip()
                    if "Фото:" in current_h2_clean:
                         clean_text = ""
                else:
                    # File missing - skip section
                    continue

            # Skip truly empty sections
            if not clean_text and not photo_match:
                continue
            
            # --- FIX CAPS ---
            if clean_text.isupper() and len(clean_text) > 4:
                clean_text = clean_text.capitalize()
            
            section_id = f"section-{section_idx}"
            if clean_text:
                quick_links_html += f'<a href="#{section_id}" class="nav-link">{clean_text}</a>\n'
                new_h2 = f'<h2 id="{section_id}" class="text-6xl font-black mb-16 tracking-tight">{clean_text}</h2>'
            else:
                new_h2 = "" # No header for this section
            
            # Replace original h2 with new one (or remove it)
            new_section_inner = re.sub(r'<h2[^>]*>.*?</h2>', new_h2, section_inner, count=1, flags=re.DOTALL)
            cleaned_memo_html += f'<section class="pt-24 border-t border-black/5">{new_section_inner}</section>\n'
            section_idx += 1
            
        modified_memo_html = cleaned_memo_html if sections_found else memo_html

        # 5. Build final page
        country_slug = filename.replace('memo-', '').replace('.html', '')
        country_page = f"{country_slug}.html" if os.path.exists(f"{country_slug}.html") else "index.html"

        new_page = template_content
        new_page = new_page.replace('██Название страны██', f"Памятка: {country_name}")
        new_page = new_page.replace('██Название██', f"Памятка: {country_name}")
        new_page = new_page.replace('██Страна██', country_name)
        new_page = new_page.replace('██country_page██', country_page)
        new_page = new_page.replace('<!-- Контент здесь -->', modified_memo_html)
        new_page = new_page.replace('<!-- Сюда вставим ссылки скриптом -->', quick_links_html)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_page)

    print(f"Success! {len(memo_files)} memo pages updated.")

if __name__ == "__main__":
    apply_template_memo()
