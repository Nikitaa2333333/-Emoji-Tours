import os
import re

def clean_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Remove sidebar links by ID (calculated by the slugifier)
    # The IDs are generated from the text.
    sidebar_ids = [
        "section-zhelaem-vam-priyatnogo-puteshestviya",
        "section-socseti-vkontakte-telegram",
        "section-individualnyj-predprinimatel-trohin-evgenij-albertovich",
        "section-" # Empty section link
    ]
    
    for sid in sidebar_ids:
        pattern = rf'<a href="#{sid}" class="nav-link">.*?</a>'
        content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)

    # 2. Remove content sections where the H2 contains the specific keywords
    # This is a broader approach than just ID matching for safety
    keywords = [
        "Желаем вам приятного путешествия",
        "Соцсети:",
        "Индивидуальный предприниматель трохин",
        "ИП Трохин"
    ]
    
    # Pattern to match a whole section block where H2 contains keywords
    # We use a pattern that matches the start of the section and looks for the keyword before the end of the section
    for kw in keywords:
        # Regex to find <section>...</section> where the inner text contains the keyword in an H2
        # Use a non-greedy match and verify the keyword is inside
        pattern = rf'<section[^>]*>(?:(?!</section>).)*?<h2[^>]*>(?:(?!</h2>).)*?{re.escape(kw)}.*?</h2>.*?建设?.*?/section>'
        # Actually, simpler: match any section that has an h2 with this stuff.
        # But section might contain other things, so we need to be careful.
        # Based on the file structure, these are separate sections.
    
    # Let's stick to the ID based one but also add a generic check for sections with these IDs
    # as Tilda's converter seems consistent with IDs.
    
    section_ids = [
        "section-zhelaem-vam-priyatnogo-puteshestviya",
        "section-socseti-vkontakte-telegram",
        "section-individualnyj-predprinimatel-trohin-evgenij-albertovich",
        "section-"
    ]
    
    for sid in section_ids:
        # Match <section ...> with the specific id in h2 and its content until </section>
        pattern = rf'<section[^>]*>(?:(?!</section>).)*?id="{sid}"(?:(?!</section>).)*?</section>'
        content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)

    # 3. Cleanup: remove section with only "/" if missed by ID (sometimes ID is section--1 etc)
    content = re.sub(r'<section[^>]*>\s*<h2[^>]*>/</h2>\s*</section>', '', content, flags=re.IGNORECASE | re.DOTALL)

    # Final cleanup of whitespaces
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Cleaned: {file_path}")

def main():
    files = [f for f in os.listdir('.') if f.endswith('.html')]
    for file in files:
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            file_content = f.read()
            # If it contains "трохин" or the specific greeting, clean it
            if 'трохин' in file_content.lower() or 'приятного путешествия' in file_content.lower():
                clean_html_file(file)

if __name__ == "__main__":
    main()
