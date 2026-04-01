import os
import re

TARGET_DIR = "."
# Обрабатываем и шаблоны, и все готовые страницы
FILES_TO_UPGRADE = [f for f in os.listdir(TARGET_DIR) if f.endswith(".html")]

MOBILE_CSS = """
    /* --- Premium Mobile Navigation Pro Max (Mobile Only) --- */
    @media (max-width: 1023px) {
        #scroll-progress {
            position: fixed; top: 0; left: 0; height: 3px;
            background: #f5e2a1; width: 0%; z-index: 1000;
            transition: width 0.1s ease-out;
            box-shadow: 0 0 10px rgba(245, 226, 161, 0.5);
        }

        .header-hidden { transform: translateY(-100%) !important; transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important; }
        .header-visible { transform: translateY(0) !important; transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important; }

        #mobile-toc-button {
            position: fixed; bottom: 30px; right: 24px; z-index: 130;
            background: #000; color: #fff; width: 64px; height: 64px;
            border-radius: 22px; display: flex; align-items: center; justify-content: center;
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            border: 1.5px solid rgba(245, 226, 161, 0.4);
        }
        #mobile-toc-button:active { scale: 0.85; }

        #mobile-drawer {
            position: fixed; bottom: 0; left: 0; width: 100%; height: 75vh;
            background: rgba(255, 252, 245, 0.95); backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            z-index: 200; border-radius: 45px 45px 0 0;
            transform: translateY(100%); transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex; flex-direction: column; padding: 30px 25px;
            border-top: 1px solid rgba(0,0,0,0.1);
            box-shadow: 0 -20px 60px rgba(0,0,0,0.15);
        }
        #mobile-drawer.open { transform: translateY(0); }
        
        #drawer-overlay {
            position: fixed; inset: 0; background: rgba(0,0,0,0.4);
            z-index: 190; opacity: 0; pointer-events: none; transition: opacity 0.5s ease;
        }
        #drawer-overlay.visible { opacity: 1; pointer-events: auto; }

        .drawer-link {
            font-size: 1.25rem; font-weight: 800; padding: 22px 0;
            color: #000 !important; border-bottom: 1.5px solid rgba(0,0,0,0.06);
            display: flex; align-items: center; justify-content: space-between;
            text-decoration: none !important;
        }
        .drawer-link::after { content: 'arrow_forward'; font-family: 'Material Symbols Outlined'; font-size: 20px; opacity: 0.2; }
    }
"""

MOBILE_HTML = """
    <!-- Premium Mobile Elements (Pro Max) -->
    <div id="scroll-progress"></div>
    <div id="drawer-overlay" onclick="toggleTOC()"></div>
    <div id="mobile-drawer">
        <div class="w-16 h-1.5 bg-black/10 rounded-full mx-auto mb-10" onclick="toggleTOC()"></div>
        <p class="text-[10px] font-black uppercase tracking-[0.4em] text-black/20 mb-8 text-center italic">Маршрут путешествия</p>
        <nav id="mobile-nav-list" class="overflow-y-auto pb-12 px-2"></nav>
    </div>
    <button id="mobile-toc-button" onclick="toggleTOC()" class="lg:hidden">
        <span class="material-symbols-outlined text-[30px]">explore</span>
    </button>
"""

MOBILE_JS = """
    <script>
        // Progress Bar logic
        window.addEventListener('scroll', () => {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            const bar = document.getElementById("scroll-progress");
            if(bar) bar.style.width = scrolled + "%";
        });

        // Smart Header logic (Auto-hide on scroll)
        let lastScrollMove = 0;
        const mainNav = document.querySelector('nav.fixed');
        window.addEventListener('scroll', () => {
            let currentScroll = window.pageYOffset || document.documentElement.scrollTop;
            if (currentScroll > lastScrollMove && currentScroll > 120) {
                mainNav.classList.add('header-hidden');
                mainNav.classList.remove('header-visible');
            } else {
                mainNav.classList.add('header-visible');
                mainNav.classList.remove('header-hidden');
            }
            lastScrollMove = currentScroll;
        });

        // Sync Sidebar to Bottom Sheet
        function toggleTOC() {
            const drw = document.getElementById('mobile-drawer');
            const ovl = document.getElementById('drawer-overlay');
            const isOpen = drw.classList.toggle('open');
            ovl.classList.toggle('visible');
            document.body.style.overflow = isOpen ? 'hidden' : '';

            if (isOpen) {
                const src = document.getElementById('quick-links');
                const dst = document.getElementById('mobile-nav-list');
                if (src && dst) {
                    dst.innerHTML = '';
                    src.querySelectorAll('.nav-link').forEach(l => {
                        const cln = l.cloneNode(true);
                        cln.className = 'drawer-link';
                        cln.onclick = (e) => {
                           toggleTOC();
                           // Ждем закрытия анимации и скроллим
                           setTimeout(() => {
                               const targetId = cln.getAttribute('href');
                               document.querySelector(targetId).scrollIntoView({behavior: 'smooth'});
                           }, 300);
                        };
                        dst.appendChild(cln);
                    });
                }
            }
        }
    </script>
"""

def upgrade_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'mobile-drawer' in content:
        return False

    # Вставка CSS
    content = content.replace('</style>', MOBILE_CSS + '</style>')
    # Вставка HTML
    content = re.sub(r'<body[^>]*>', lambda m: m.group(0) + MOBILE_HTML, content)
    # Вставка JS
    content = content.replace('</body>', MOBILE_JS + '</body>')

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

if __name__ == "__main__":
    print("🚀 Premium Upgrade Script Created!")
    count = 0
    for f_name in FILES_TO_UPGRADE:
        if upgrade_file(f_name):
            print(f"✅ Enhanced: {f_name}")
            count += 1
    print(f"🎉 Total files upgraded: {count}")
