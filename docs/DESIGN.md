# Design System Strategy: Emoji Tours

## 1. Overview & Creative North Star
The design system for "Emoji Tours" is anchored by a Creative North Star we call **"The Sunlit Editorial."** 

Unlike traditional travel portals that feel cluttered and transactional, this system treats the digital interface as a high-end travel magazine brought to life. It prioritizes emotional resonance over information density. We achieve this through "The Breathing Layout"—intentional asymmetry where text and high-resolution photography dance across the screen, utilizing expansive white space (up to `24` on our spacing scale) to allow the user's mind to wander. 

The aesthetic is bright, airy, and human-centric. By blending the geometric precision of the **Manrope** typeface with soft, organic rounded corners (`xl: 3rem`), we create an environment that feels both professional and deeply welcoming.

## 2. Colors
Our palette is a sophisticated play on light and warmth. We avoid the "default" feel by using an off-white, warm foundation (`background: #fff9ed`) instead of pure white, which reduces eye strain and evokes the feel of premium paper.

*   **The "No-Line" Rule:** Sectioning must never be achieved with 1px solid borders. To separate content, designers must use tonal shifts. For example, a card might use `surface-container-low` against a `surface` background.
*   **Surface Hierarchy & Nesting:** Treat the UI as layers of fine material. A "Hero" section might sit on `surface`, while a "Booking Widget" floats above it using `surface-container-highest` with a backdrop blur.
*   **The "Glass & Gradient" Rule:** To move beyond static colors, primary CTAs should utilize a subtle linear gradient from `primary` (#6b5f25) to `primary_container` (#f4e29b). This adds a "glow" effect that feels high-end.
*   **Signature Textures:** Use semi-transparent overlays (`surface_variant` at 40% opacity) over professional photography to ensure legibility while maintaining the "airy" feel of the image.

## 3. Typography: Manrope (Cyrillic)
Typography is our primary tool for authority. By using Manrope’s wide, modern letterforms, we convey a sense of reliability and contemporary flair.

*   **Display (Display-lg to sm):** Used for emotional hooks in Russian (e.g., "Открой мир заново"). These should be set with tight letter-spacing (-0.02em) to feel like a magazine masthead.
*   **Headlines (Headline-lg to md):** Your primary narrative tool. Use `on_surface` (#363225) for high contrast against the pastel background.
*   **Body (Body-lg to md):** Reserved for storytelling. Ensure line-height is generous (1.5x - 1.6x) to maintain the airy aesthetic.
*   **Labels (Label-md):** Used for metadata (e.g., "5 дней / 4 ночи"). These can be uppercase with slight letter-spacing to distinguish them from body copy.

## 4. Elevation & Depth
We reject traditional drop shadows in favor of **Tonal Layering**.

*   **The Layering Principle:** Place a `surface-container-lowest` card on a `surface-container-low` section. This creates a soft, natural "lift" that mimics physical paper stacked on a desk.
*   **Ambient Shadows:** For floating elements like a "Book Now" sticky button, use an extra-diffused shadow: `box-shadow: 0 20px 40px rgba(54, 50, 37, 0.06)`. The color is a tinted version of `on_surface`, making the shadow feel like it belongs to the environment.
*   **The "Ghost Border":** If a boundary is strictly required for accessibility, use the `outline_variant` token at 15% opacity. It should be felt, not seen.
*   **Glassmorphism:** Navigation bars and modal overlays must use `backdrop-blur: 12px` combined with a semi-transparent `surface` color. This keeps the "airy" travel photography visible even when UI elements are on top.

## 5. Components

### Buttons
*   **Primary:** High-impact. Soft pastel yellow (`primary_container`) with `on_primary_container` text. Roundedness: `full`. No shadow, but a subtle scale-up (1.02x) on hover.
*   **Secondary:** Ghost style. `outline` color for text, with a `surface_container_low` background that only appears on hover.

### Cards (Tour Previews)
*   **Forbid Dividers:** Do not use lines to separate the image from the price or title. Use vertical white space (`spacing: 4`) and typography scale to create the break.
*   **Styling:** Large `xl` (3rem) corner radius on the top-left and bottom-right corners only to create a "signature" asymmetric look inspired by high-end editorial layouts.

### Chips & Tags
*   **Travel Tags:** Use `secondary_container` with `on_secondary_container` text for tags like "Gourmet Tour" or "Active Rest." These should be small (`label-sm`) and pill-shaped.

### Input Fields
*   **Search/Booking Inputs:** Minimalist. No bottom line or full box. Use a `surface_container_low` background with a `sm` (0.5rem) corner radius. The label should float above the field in `body-sm`.

### Image Containers
*   Every image must feature a subtle inner "glow" or a rounded corner of at least `lg` (2rem). In hero sections, use overlapping images where one smaller image (e.g., a detail shot) sits 15% over the edge of a larger landscape shot.

## 6. Do's and Don'ts

### Do
*   **DO** use Russian punctuation correctly (e.g., using "—" instead of "-").
*   **DO** leave at least `20` (7rem) of vertical space between major content blocks.
*   **DO** use professional, high-brightness photography with warm color grading.
*   **DO** treat text as part of the composition—wrap text around images in an asymmetrical fashion.

### Don't
*   **DON'T** use 100% black (#000000). Use `on_surface` (#363225) for all dark elements to maintain the "soft" feel.
*   **DON'T** use 90-degree corners. Everything must have a minimum of `sm` (0.5rem) rounding to remain "emotional" and "approachable."
*   **DON'T** use standard grid layouts where everything is perfectly aligned in columns. Intentionally offset one or two elements to break the "template" look.