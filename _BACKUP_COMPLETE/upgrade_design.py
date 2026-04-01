import os
import re

# Папка с файлами сайта
TARGET_DIR = r"c:\Users\User\Downloads\tilda dododo"
TEMPLATE_FILE = os.path.join(TARGET_DIR, 'template.html')

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def get_block(content, start_marker, end_marker):
    pattern = re.escape(start_marker) + r'.*?' + re.escape(end_marker)
    match = re.search(pattern, content, flags=re.DOTALL)
    if match:
        return match.group(0)
    return None

def update_file(filepath, template_content):
    content = read_file(filepath)
    original_content = content
    
    print(f"⚙️  Обработка: {os.path.basename(filepath)}")
    
    # 1. Замена шапки
    nav_start = '<!-- ═══ ФИКСИРОВАННАЯ ШАПКА ═══ -->'
    nav_end = '</nav>'
    new_nav = get_block(template_content, nav_start, nav_end)
    if new_nav:
        content = re.sub(re.escape(nav_start) + r'.*?' + re.escape(nav_end), new_nav.replace('\\', r'\\'), content, flags=re.DOTALL)
        
    # 2. Замена подвала
    footer_start = '<footer'
    footer_end = '</footer>'
    new_footer = get_block(template_content, footer_start, footer_end)
    if new_footer:
        content = re.sub(re.escape(footer_start) + r'.*?' + re.escape(footer_end), new_footer.replace('\\', r'\\'), content, flags=re.DOTALL)
        
    # 3. Замена стилей (для иконок wght: 300)
    style_start = '<style>'
    style_end = '</style>'
    new_style = get_block(template_content, style_start, style_end)
    if new_style:
        content = re.sub(re.escape(style_start) + r'.*?' + re.escape(style_end), new_style.replace('\\', r'\\'), content, flags=re.DOTALL)
        
    # 4. Замена формы с сохранением текущей Страны в инпуте!
    form_start = '<!-- ═══ ФОРМА (ШАБЛОН) ═══ -->'
    form_end = '</section>'
    
    old_form = get_block(content, form_start, form_end)
    new_form_template = get_block(template_content, form_start, form_end)
    
    if old_form and new_form_template:
        # Ищем текущее сохраненное значение в input "Направление"
        # Например: value="Египет"
        old_value_match = re.search(r'value="([^"]+)"\s+type="text"', old_form)
        if old_value_match:
            country_name = old_value_match.group(1)
            # Вставляем имя страны из старой формы в новый шаблон формы
            injected_form = new_form_template.replace('██Страна██', country_name)
            content = re.sub(re.escape(form_start) + r'.*?' + re.escape(form_end), injected_form.replace('\\', r'\\'), content, flags=re.DOTALL)
            
    if content != original_content:
        write_file(filepath, content)
        print(f"✅ Обновлен: {os.path.basename(filepath)}")
    else:
        print(f"➖ Без изменений: {os.path.basename(filepath)}")

def main():
    if not os.path.exists(TEMPLATE_FILE):
        print(f"❌ Шаблон не найден: {TEMPLATE_FILE}")
        return
        
    template_content = read_file(TEMPLATE_FILE)
    print("🚀 Начинаем обновление дизайна (Pro Max)...")
    
    for filename in os.listdir(TARGET_DIR):
        # Проходим только по html страницам, кроме главной и самого шаблона
        if filename.endswith('.html') and filename not in ['index.html', 'template.html']:
            filepath = os.path.join(TARGET_DIR, filename)
            update_file(filepath, template_content)
    
    print("🎉 Обновление завершено! Текст стран 100% сохранен.")

if __name__ == "__main__":
    main()
