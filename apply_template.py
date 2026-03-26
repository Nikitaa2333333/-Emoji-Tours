import os
import re

def apply_template():
    template_path = 'template.html'
    if not os.path.exists(template_path):
        print(f"Error: {template_path} not found.")
        return

    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()

    # Get the country files (exclude index, template, memo-)
    html_files = [f for f in os.listdir('.') if f.endswith('.html') 
                  and f not in ['index.html', 'template.html'] 
                  and not f.startswith('memo-')]

    for filename in html_files:
        print(f"Processing {filename}...")
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Extract Country Name
        # Try to find #page-title first
        title_match = re.search(r'id="page-title"[^>]*>(.*?)</h1>', content, re.DOTALL)
        if title_match:
            country_name = title_match.group(1).strip()
        else:
            # Fallback to <title>
            title_tag_match = re.search(r'<title>(.*?) — Emoji Tours</title>', content)
            if title_tag_match:
                country_name = title_tag_match.group(1).strip()
            else:
                country_name = filename.replace('.html', '').capitalize()

        # 2. Extract Hero Image
        hero_match = re.search(r'id="hero-image"[^>]*src="(.*?)"', content)
        hero_src = hero_match.group(1) if hero_match else "placeholder_hero.jpg"

        # 3. Extract Memo Content
        # We look for the content inside #memo-content-area
        memo_area_match = re.search(r'id="memo-content-area"[^>]*>(.*?)</div>\s*<!-- ═══ ФОРМА', content, re.DOTALL)
        if not memo_area_match:
            # alternative search if comment is different
            memo_area_match = re.search(r'id="memo-content-area"[^>]*>(.*?)</div>\s*<section id="booking-form"', content, re.DOTALL)
        
        memo_html = memo_area_match.group(1).strip() if memo_area_match else "<!-- No content found -->"

        # 4. Extract Slug/Memo link
        memo_link_match = re.search(r'href="(memo-.*?\.html)"', content)
        memo_slug_link = memo_link_match.group(1) if memo_link_match else "#"
        memo_slug = memo_slug_link.replace('memo-', '').replace('.html', '')

        # 5. Extract H2s for sub-navigation
        h2_matches = re.findall(r'<h2[^>]*>(.*?)</h2>', memo_html)
        quick_links_html = ""
        # We need to add IDs to H2s in the content area for smooth scroll to work
        # Let's do a simple replacement for H2s to include IDs
        for i, h2_text in enumerate(h2_matches):
            section_id = f"section-{i}"
            # Clean up text from tags if any
            clean_text = re.sub(r'<[^>]+>', '', h2_text).strip()
            quick_links_html += f'<a href="#{section_id}" class="text-sm text-on-surface-variant hover:text-primary transition-colors">{clean_text}</a>\n'
            
            # Replace the first occurrence of this H2 in memo_html with an ID-labeled one
            memo_html = memo_html.replace(f'h2 class="text-6xl font-black mb-16 tracking-tight">{h2_text}</h2>', 
                                          f'h2 id="{section_id}" class="text-6xl font-black mb-16 tracking-tight">{h2_text}</h2>', 1)
            # handle other possible classes
            memo_html = memo_html.replace(f'<h2>{h2_text}</h2>', f'<h2 id="{section_id}">{h2_text}</h2>', 1)

        # Build final page
        new_page = template_content
        new_page = new_page.replace('██Название страны██', f"{country_name}")
        new_page = new_page.replace('██Название██', country_name)
        new_page = new_page.replace('██hero.jpg██', hero_src)
        new_page = new_page.replace('██slug██', memo_slug)
        new_page = new_page.replace('██Страна██', country_name)
        new_page = new_page.replace('<!-- Контент здесь -->', memo_html)
        new_page = new_page.replace('<!-- Будет заполнено скриптом из h2 заголовков -->', quick_links_html)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_page)

    print("Successfully updated all country pages.")

if __name__ == "__main__":
    apply_template()
