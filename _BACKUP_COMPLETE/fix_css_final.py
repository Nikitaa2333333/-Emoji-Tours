import os
import re

CLEAN_NAVIGATION_STYLE = """
        .nav-link {
            display: block;
            padding: 0.6rem 1.5rem;
            border-left: 2px solid transparent;
            font-size: 0.85rem;
            line-height: 1.3;
            color: #4b4b4b;
            transition: all 0.2s ease;
        }

        .nav-link:hover {
            color: #000;
            background: rgba(245, 226, 161, 0.1);
        }

        .nav-link.active {
            color: #000;
            font-weight: 700;
            border-left-color: #f5e2a1;
            background: rgba(245, 226, 161, 0.2);
        }

        .header-hidden { transform: translateY(-100%) !important; transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important; }
        .header-visible { transform: translateY(0) !important; transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important; }

        @media (max-width: 1023px) {
            #scroll-progress {
                position: fixed; top: 0; left: 0; height: 3px;
                background: #f5e2a1; width: 0%; z-index: 1000;
                transition: width 0.1s ease-out;
                box-shadow: 0 0 10px rgba(245, 226, 161, 0.5);
            }

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

        @media (min-width: 1024px) { 
            #nav-navigation-trigger, 
            #nav-navigation-container, 
            #nav-overlay, 
            #nav-bottom-sheet, 
            #mobile-toc-button,
            #mobile-drawer,
            #drawer-overlay,
            #scroll-progress { 
                display: none !important; 
            } 
        }
"""

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False

    original_content = content

    # Replace everything between the start of .nav-link and the end of </style>
    # or between #quick-links and </style>
    
    # We look for a known starting point in the navigation styles
    start_point = content.find('.nav-link {')
    if start_point == -1:
        # Try alternative start point
        start_point = content.find('/* Стили навигации')
    
    end_point = content.find('</style>')
    
    if start_point != -1 and end_point != -1 and start_point < end_point:
        new_content = content[:start_point] + CLEAN_NAVIGATION_STYLE + content[end_point:]
        content = new_content

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Execution
path = os.getcwd()
files_updated = []
for filename in os.listdir(path):
    if filename.endswith('.html'):
        if process_file(filename):
            files_updated.append(filename)

print(f"Navigation styles fixed in {len(files_updated)} files.")
