import os
import re

def clean_memo_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Remove the link in the sidebar/quick-links
    # Pattern: <a href="#section-socseti-vkontakte-instagram-telegram" class="nav-link">Соцсети: вконтакте | instagram | telegram</a>
    # We use a more flexible regex to catch variations if any
    content = re.sub(r'<a[^>]*href="#section-socseti[^>]*>.*?</a>\s*', '', content, flags=re.DOTALL)

    # 2. Remove the section in the main content
    # Pattern: <section class="pt-12 border-t border-black/5"><h2 id="section-socseti-vkontakte-instagram-telegram"[^>]*>Соцсети: вконтакте | instagram | telegram</h2>([ \t]*<div[^>]*>.*?</div>)?\s*</section>
    # Note: Sometimes there might be a div with text inside the section, sometimes not.
    content = re.sub(r'<section[^>]*>\s*<h2[^>]*id="section-socseti[^>]*>.*?</h2>\s*</section>\s*', '', content, flags=re.DOTALL)
    
    # Let's also check for cases where it's wrapped in a div but without the section structure if any
    # Or just the h2 if it's not in a section
    content = re.sub(r'<h2[^>]*id="section-socseti[^>]*>.*?</h2>\s*', '', content, flags=re.DOTALL)

    # Also clean up the phone/address junk if they are right next to it and look like the agency info
    # The user screenshot showed just the social media, but usually they come together.
    # For now, let's stick to what's requested to be safe, but I'll add the others if they match the "agency info" pattern.
    
    # Specifically remove:
    # <section class="pt-12 border-t border-black/5"><h2 id="section-telefon-7-977-730-95-22" class="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-[1.1] md:leading-none">Телефон: +7 (977) 730 95 22</h2></section>
    content = re.sub(r'<section[^>]*>\s*<h2[^>]*id="section-telefon-7-977-730-95-22"[^>]*>.*?</h2>\s*</section>\s*', '', content, flags=re.DOTALL)
    content = re.sub(r'<a[^>]*href="#section-telefon-7-977-730-95-22"[^>]*>.*?</a>\s*', '', content, flags=re.DOTALL)

    # <section class="pt-12 border-t border-black/5"><h2 id="section-gorod-moskva-scherbinka-ul-yubilejnaya-d-3a" class="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-[1.1] md:leading-none">Город москва, щербинка ул. юбилейная д.3а</h2></section>
    content = re.sub(r'<section[^>]*>\s*<h2[^>]*id="section-gorod-moskva-scherbinka[^>]*>.*?</h2>\s*</section>\s*', '', content, flags=re.DOTALL)
    content = re.sub(r'<a[^>]*href="#section-gorod-moskva-scherbinka[^>]*>.*?</a>\s*', '', content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Cleaned {file_path}")

def main():
    directory = "."
    for filename in os.listdir(directory):
        if filename.startswith("memo-") and filename.endswith(".html"):
            clean_memo_file(os.path.join(directory, filename))

if __name__ == "__main__":
    main()
