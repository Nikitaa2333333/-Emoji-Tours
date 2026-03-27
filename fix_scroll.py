import os
import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = False

    # 1. Исправляем scroll-padding-top в CSS
    # Сначала удаляем старый, если он был, чтобы не дублировать
    content = re.sub(r'scroll-padding-top:\s*[^;]+;', '', content)
    
    if 'scroll-behavior: smooth;' in content:
        content = content.replace('scroll-behavior: smooth;', 'scroll-behavior: smooth; scroll-padding-top: 110px;')
        changed = True
    elif '</style>' in content:
        content = content.replace('</style>', '        html { scroll-behavior: smooth; scroll-padding-top: 110px; }\n    </style>')
        changed = True

    # 2. Исправляем JS scrollTo на scrollIntoView
    pattern = r'window\.scrollTo\(\s*\{\s*top:\s*target\.offsetTop\s*-\s*\d+,\s*behavior:\s*\'smooth\'\s*\}\s*\);?'
    replacement = "target.scrollIntoView({ behavior: 'smooth' });"
    
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        changed = True

    # 3. Автоматическая простановка ID для секций (Западное, Южное, Восточное побережья и О стране)
    sections = {
        'О стране': 'section-о-стране',
        'Западное побережье': 'section-западное-побережье',
        'Южное побережье': 'section-южное-побережье',
        'Восточное побережье': 'section-восточное-побережье'
    }

    for text, section_id in sections.items():
        # Ищем либо p либо h2 с таким текстом, у которого нет id
        # <p class="...">Текст</p>  =>  <h2 id="..." class="...">Текст</h2>
        # <h2 class="...">Текст</h2> =>  <h2 id="..." class="...">Текст</h2>
        
        # Паттерн ищет тег <p> или <h2> содержащий текст секции, но без id
        node_pattern = rf'<(p|h2)([^>]+)>({text})</\1>'
        if re.search(node_pattern, content):
            # Заменяем на h2 с id
            node_replacement = rf'<h2 id="{section_id}"\2>\3</h2>'
            content = re.sub(node_pattern, node_replacement, content)
            changed = True

    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    root = '.'
    fixed_count = 0
    # Обрабатываем все html файлы
    for filename in os.listdir(root):
        if filename.endswith('.html') and filename != 'index.html': # Пропускаем главную
            if fix_file(os.path.join(root, filename)):
                print(f"Исправлен: {filename}")
                fixed_count += 1
    print(f"Готово. Исправлено файлов: {fixed_count}")

if __name__ == "__main__":
    main()
