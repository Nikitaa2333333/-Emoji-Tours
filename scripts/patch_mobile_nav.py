import os
import re

def patch_file(file_path):
    print(f"Обработка {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Проверка на идемпотентность
    if '// 1. Популяция мобильного меню' in content:
        print(f"  - Файл уже пропатчен.")
        return

    # Код для вставки
    injection = """      // 1. Популяция мобильного меню из десктопного
      const mobileQuickLinks = document.getElementById('mobile-quick-links');
      const desktopLinksSource = document.querySelectorAll('#quick-links .nav-link');
      
      if (mobileQuickLinks && desktopLinksSource.length > 0) {
        mobileQuickLinks.innerHTML = '';
        desktopLinksSource.forEach(link => {
          const mobileLink = link.cloneNode(true);
          // Стили для мобильного меню (крупнее, жирнее)
          mobileLink.className = 'text-[22px] font-black py-2 hover:text-primary transition-colors';
          mobileLink.onclick = () => {
            toggleMenu();
            // Плавный скролл уже есть в общем скрипте
          };
          mobileQuickLinks.appendChild(mobileLink);
        });
      }
"""
    
    # Ищем точку входа
    pattern = r"document\.addEventListener\('DOMContentLoaded', \(\) => \{"
    if re.search(pattern, content):
        new_content = re.sub(pattern, f"document.addEventListener('DOMContentLoaded', () => {{\n{injection}", content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  + Успешно пропатчен.")
    else:
        print(f"  ! Точка входа не найдена.")

def main():
    base_dirs = ['pages/memos', 'pages/countries']
    for b_dir in base_dirs:
        if os.path.exists(b_dir):
            for f in os.listdir(b_dir):
                if f.endswith('.html'):
                    patch_file(os.path.join(b_dir, f))

if __name__ == "__main__":
    main()
