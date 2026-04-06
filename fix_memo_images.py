"""
Fix memo page images by matching them to the correct sections
based on the original Tilda source HTML anchor names.
"""
import re
import os

MEMO_DIR = 'pages/memos'
TILDA_DIR = 'pages'

# Map new section IDs → Tilda anchor names
# (keywords that appear in section ID → anchor name)
SECTION_TO_ANCHOR = {
    'pered-otezdom': 'BEFORELEAVING',
    'sobiraya-bagazh': 'CollectingLuggage',
    'registratsiya-na-rejs': 'Checkinbaggage',
    'tamozhennyj-kontrol': lambda country: f'{country}CUSTOMCONTROL',
    'pasportnyj-kontrol-viza': lambda country: f'{country}PASSPORTCONTROL',
    'v-aeroportu-': lambda country: f'{country}airport',
    'pravila-lichnoj-gigieny': 'THERULESOFPERSONALHYGIENEANDSAFETY',
    'v-sluchae-poteri-pasporta': 'INCASEOFLOSSOFPASSPORT',
}

# Map new memo filename → Tilda source filename + country anchor key
COUNTRY_MAP = {
    'china': ('memochina', 'China'),
    'cuba': ('memocuba', 'Cuba'),
    'dominikana': ('memodominikana', 'Dominikana'),
    'egypt': ('memoegypt', 'Egypt'),
    'india': ('memoindia', 'India'),
    'indonesia': ('memoindonesia', 'Indonesia'),
    'israel': ('memoisrael', 'Israel'),
    'maldives': ('memomaldives', 'Maldives'),
    'mauritius': ('memomauritius', 'Mauritius'),
    'mexico': ('memomexico', 'Mexico'),
    'oae': ('memooae', 'OAE'),
    'ofcyprus': ('memoofcyprus', 'Cyprus'),
    'seychelles': ('memoseyshelles', 'Seychelles'),
    'seyshelles': ('memoseyshelles', 'Seychelles'),
    'sri-lanka': ('memosrilanka', 'SriLanka'),
    'srilanka': ('memosrilanka', 'SriLanka'),
    'tanzania': ('memotanzania', 'Tanzania'),
    'thailand': ('memothailand', 'Thailand'),
    'touriststravelingtoturkey': ('touriststravelingtoturkey', 'Turkey'),
    'tunisia': ('memotunisia', 'Tunisia'),
    'turkey': ('touriststravelingtoturkey', 'Turkey'),
    'vietnam': ('memovietnam', 'Vietnam'),
}


def extract_tilda_anchor_images(tilda_html):
    """
    From a Tilda HTML, extract a dict: anchor_name -> [image_filename, ...]
    Images are grouped under the anchor that precedes them.
    """
    # Find all anchors and their positions
    anchor_pattern = re.compile(r'name="([A-Z][^"]*)"')
    img_pattern = re.compile(r'(tild[a-f0-9-]{20,}__[^\s"<>]+\.(?:jpg|jpeg|png|webp))')

    # Since the Tilda HTML is mostly one long line, we work with positions
    anchors = [(m.start(), m.group(1)) for m in anchor_pattern.finditer(tilda_html)]
    images = [(m.start(), m.group(1)) for m in img_pattern.finditer(tilda_html)]

    if not anchors:
        return {}

    # For each anchor, find images between it and the next anchor
    result = {}
    for i, (anchor_pos, anchor_name) in enumerate(anchors):
        next_pos = anchors[i + 1][0] if i + 1 < len(anchors) else len(tilda_html)
        # Find images in this range (deduplicated, preserving order)
        seen = set()
        imgs_in_range = []
        for img_pos, img_file in images:
            if anchor_pos <= img_pos < next_pos:
                # Strip the empty/lazy variant prefix
                clean = re.sub(r'-__empty__', '', img_file)
                # Deduplicate (Tilda has src + data-original for same image)
                if clean not in seen:
                    seen.add(clean)
                    imgs_in_range.append(clean)
        if imgs_in_range:
            result[anchor_name] = imgs_in_range

    return result


def find_tilda_anchor_for_section(section_id, country_key):
    """
    Given a new section ID and country key (e.g. 'Egypt'),
    return the matching Tilda anchor name.
    """
    sid = section_id.lower()

    # Direct matches
    for pattern, anchor in SECTION_TO_ANCHOR.items():
        if pattern in sid:
            if callable(anchor):
                return anchor(country_key)
            return anchor

    # Country section (e.g. "egipet", "korolevstvo-tailand", "tunisiya")
    # These map to the country anchor (e.g. "Egypt", "Thailand", "Tunisia")
    # We can't easily match these, so return None
    return None


def get_section_img_tags(html):
    """
    Extract list of (section_id, full_src, filename) from new memo HTML.
    Uses positional approach: each image belongs to the last-opened section.
    """
    section_open_re = re.compile(r'<section[^>]+id="([^"]+)"')
    img_re = re.compile(r'src="((?:\.\./)+images/(tild[a-f0-9-]{20,}__[^"]+\.(?:jpg|jpeg|png|webp)))"')

    # Build list of events: (pos, type, value)
    events = []
    for m in section_open_re.finditer(html):
        events.append((m.start(), 'section', m.group(1)))
    for m in img_re.finditer(html):
        events.append((m.start(), 'img', (m.group(1), m.group(2))))

    events.sort(key=lambda e: e[0])

    results = []
    current_section = None
    for pos, etype, val in events:
        if etype == 'section':
            current_section = val
        elif etype == 'img' and current_section:
            full_src, filename = val
            results.append((current_section, full_src, filename))

    return results


def fix_memo_file(new_path, tilda_path, country_key, dry_run=True):
    with open(new_path, 'r', encoding='utf-8') as f:
        new_html = f.read()
    with open(tilda_path, 'r', encoding='utf-8') as f:
        tilda_html = f.read()

    tilda_map = extract_tilda_anchor_images(tilda_html)
    section_imgs = get_section_img_tags(new_html)

    fixes = []
    for section_id, current_full_src, current_filename in section_imgs:
        anchor = find_tilda_anchor_for_section(section_id, country_key)
        if anchor and anchor in tilda_map:
            correct_imgs = tilda_map[anchor]
            correct_filename = correct_imgs[0]  # Use first image for the section

            if current_filename != correct_filename:
                # Build the new src path
                new_src = re.sub(r'tild[^"]+\.(jpg|jpeg|png|webp)',
                                 correct_filename, current_full_src)
                fixes.append((section_id, current_full_src, new_src,
                               current_filename, correct_filename))

    if fixes:
        print(f"\n{os.path.basename(new_path)}:")
        for section_id, old_src, new_src, old_file, new_file in fixes:
            print(f"  [{section_id}]")
            print(f"    WAS: {old_file}")
            print(f"    NOW: {new_file}")

            if not dry_run:
                new_html = new_html.replace(old_src, new_src, 1)

        if not dry_run:
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(new_html)
            print(f"  OK Saved")
    else:
        print(f"\n{os.path.basename(new_path)}: no fixes needed")

    return fixes


def main(dry_run=True):
    if dry_run:
        print("=== DRY RUN (no files changed) ===\n")
    else:
        print("=== APPLYING FIXES ===\n")

    total_fixes = 0
    for memo_file in sorted(os.listdir(MEMO_DIR)):
        if not memo_file.endswith('.html'):
            continue
        country = memo_file.replace('.html', '')
        if country not in COUNTRY_MAP:
            continue

        tilda_name, country_key = COUNTRY_MAP[country]
        tilda_path = os.path.join(TILDA_DIR, tilda_name + '.html')
        new_path = os.path.join(MEMO_DIR, memo_file)

        if not os.path.exists(tilda_path):
            print(f"\n{memo_file}: Tilda source not found ({tilda_path})")
            continue

        fixes = fix_memo_file(new_path, tilda_path, country_key, dry_run=dry_run)
        total_fixes += len(fixes)

    print(f"\n{'='*40}")
    print(f"Total fixes: {total_fixes}")
    if dry_run:
        print("Run with dry_run=False to apply changes.")


if __name__ == '__main__':
    import sys
    apply = '--apply' in sys.argv
    main(dry_run=not apply)
