import os
import re

def fix_memo_file(filepath):
    print(f"Processing {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Fix H1 overlapping (ensure it has leading-[1.1] instead of leading-none)
    # H1 is unique in each memo page header
    content = re.sub(
        r'(<h1[^>]*class="[^"]*)leading-none([^"]*")',
        r'\1leading-[1.1]\2',
        content
    )

    # 2. Fix the duplicate closing divs before the FORM comment
    # This is the primary layout-breaker
    form_comment = r'<!-- ═══ ФОРМА \(ШАБЛОН\) ═══ -->'
    pattern_duplicate_divs = r'(</div>\s*</div>\s*</div>)\s*' + form_comment + r'\s*(</div>\s*</div>\s*</div>)'
    content = re.sub(pattern_duplicate_divs, r'\1\n\n  ' + form_comment, content, flags=re.DOTALL)

    # 3. Fix embassy and contact sections
    # Often they have redundant closing tags after the "grid grid-cols-1 gap-8" block
    content = re.sub(
        r'(<div class="grid grid-cols-1 gap-8">.*?</div>\s*</div>\s*</div>)\s*</div>',
        r'\1',
        content,
        flags=re.DOTALL
    )

    # 4. Convert technical H2 headers (emails, websites, names) to P tags for better layout
    # And fix their massive sizes
    keywords = ['@', 'www.', 'rusemb', 'embassy', 'сайт:', 'е-mail:', 'посол:', 'генконсул:', 'заведующий:', 'тел.']
    
    def process_h2(match):
        h2_content = match.group(2)
        h2_inner_text = re.sub(r'<[^>]+>', '', h2_content).lower()
        
        if any(key in h2_inner_text for key in keywords):
            # Convert to P with consistent styling
            # Using text-2xl/3xl and font-black for clarity without breaking layout
            return f'<p class="text-2xl md:text-3xl font-black mb-4 tracking-tight leading-relaxed">{h2_content}</p>'
        return match.group(0)

    content = re.sub(r'(<h2[^>]*>)(.*?)(</h2>)', process_h2, content, flags=re.DOTALL)

    # 5. Fix capitalization of cities in embassy titles (simple list for now)
    cities = {
        'ханой': 'Ханой',
        'дананг': 'Дананг',
        'коломбо': 'Коломбо',
        'хургада': 'Хургада',
        'каир': 'Каир',
        'мале': 'Мале',
        'банкок': 'Бангкок',
        'дубай': 'Дубай'
    }
    for lower_c, upper_c in cities.items():
        content = content.replace(f'в г. {lower_c}', f'в г. {upper_c}')
        content = content.replace(f'г. {lower_c}', f'г. {upper_c}')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Finished {filepath}")

def main():
    files = [f for f in os.listdir('.') if f.startswith('memo-') and f.endswith('.html')]
    for f in files:
        fix_memo_file(f)

if __name__ == "__main__":
    main()
