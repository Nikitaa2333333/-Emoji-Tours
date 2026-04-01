import os
import re
from bs4 import BeautifulSoup

def update_country_page(filepath):
    print(f"Processing country page: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    filename = os.path.basename(filepath)
    slug = filename.replace('.html', '')
    memo_url = f"memo-{slug}.html"

    # 1. Update Sidebar
    sidebar_nav = soup.find('nav', id='quick-links')
    if sidebar_nav:
        links = sidebar_nav.find_all('a', class_='nav-link')
        has_memo = any(memo_url in a.get('href', '') for a in links)
        if not has_memo:
            # Find "О стране" link
            o_strane = None
            for a in links:
                if "О стране" in a.get_text():
                    o_strane = a
                    break
            
            new_link = soup.new_tag('a', href=memo_url, attrs={'class': 'nav-link'})
            new_link.string = "Памятка туристу"
            
            if o_strane:
                o_strane.insert_after(new_link)
                print(f"  - Added Memo link to sidebar after 'О стране'")
            else:
                sidebar_nav.insert(0, new_link)
                print(f"  - Added Memo link to start of sidebar")

    # 2. Update JS for Bottom Sheet (Regex-based for JS is safer than BS4)
    # We want to inject the memo link into the list.innerHTML generation
    js_pattern = re.compile(r'(function generateLinks\(elements\) \{.*?list\.innerHTML = \'\';)', re.DOTALL)
    if js_pattern.search(html):
        memo_injection = f"\n    // Добавляем ссылку на памятку\n    const memoLink = document.createElement('a');\n    memoLink.className = 'nav-link-item';\n    memoLink.href = '{memo_url}';\n    memoLink.innerHTML = `<span>Памятка туристу</span><svg width=\"20\" height=\"20\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M5 12h14m-7-7 7 7-7 7\"/></svg>`;\n    list.appendChild(memoLink);\n"
        
        # Avoid duplicate injection
        if f"href = '{memo_url}'" not in html:
            html = js_pattern.sub(r'\1' + memo_injection, html)
            print(f"  - Injected Memo link into Bottom Sheet JS")

    # 3. Fix scroll logic in Bottom Sheet JS (ensure it doesn't prevent default on normal links)
    scroll_fix_pattern = re.compile(r'link\.onclick = \(e\) => \{.*?e\.preventDefault\(\);.*?const target = document\.getElementById\(h\.id\);', re.DOTALL)
    # This part is harder with regex, let's keep it simple for now or use a different approach.

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup) if not js_pattern.search(html) else html) # If regex was used, use modified html string

def update_memo_page(filepath):
    print(f"Processing memo page: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Sidebar
    soup = BeautifulSoup(content, 'html.parser')
    sidebar_nav = soup.find('nav', id='quick-links')
    if sidebar_nav:
        links = sidebar_nav.find_all('a', class_='nav-link')
        has_title = any("#page-title" in a.get('href', '') for a in links)
        if not has_title:
            h1 = soup.find('h1')
            title_text = h1.get_text().strip() if h1 else "Памятка"
            # Извлекаем название страны из "Памятка: Египет"
            country_match = re.search(r'Памятка:\s*(.*)', title_text)
            if country_match:
                sidebar_text = f"{country_match.group(1).split()[0]}-Памятка"
            else:
                sidebar_text = title_text
                
            new_link = soup.new_tag('a', href="#page-title", attrs={'class': 'nav-link'})
            new_link.string = sidebar_text
            sidebar_nav.insert(0, new_link)
            print(f"  - Added {sidebar_text} link to sidebar")

    # 2. Update JS for Bottom Sheet
    # Change querySelectorAll('h2') to Array.from(document.querySelectorAll('h1, h2'))
    content = content.replace("const headings = document.querySelectorAll('h2');", "const headings = Array.from(document.querySelectorAll('h1, h2'));")
    # Also handle h1 in the loop if needed (BS4 already updated the ID if missing)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup)) # Write updated sidebar
        
    # Re-open and apply string replacements for JS which BS4 might mess up
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace("const headings = document.querySelectorAll('h2');", "const headings = Array.from(document.querySelectorAll('h1, h2'));")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    files = os.listdir('.')
    for f in files:
        if f.endswith('.html') and not f.startswith('index') and not f.startswith('template'):
            if f.startswith('memo-'):
                update_memo_page(f)
            else:
                # Check if it's a country page (not dashboard, etc)
                # Usually name is just word.html
                if '-' not in f:
                    update_country_page(f)

if __name__ == "__main__":
    main()
