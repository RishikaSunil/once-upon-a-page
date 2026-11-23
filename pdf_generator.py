"""
pdf_generator.py - Storybook PDF Generator
Creates a professionally designed, illustrated children's picture book PDF.
Includes:
1. Illustrated Front Cover with original book cover, title, author and ornaments.
2. All story chapters in sequential order:
   - Left Page: Full high-resolution scene illustration with decorative frame and chapter tag.
   - Right Page: Cream paper texture, chapter heading, story prose, dialogue, moral card, and page numbers.
3. Final story page with ending illustration and 'The End' enchanted seal.
"""

import os
import io
import re
import html
import urllib.request
from PIL import Image, ImageDraw, ImageFont

PAGE_W = 800
PAGE_H = 1040

def get_font(size, bold=False, italic=False):
    """Retrieve bundled Georgia serif fonts with fallbacks."""
    f_name = 'georgiab.ttf' if bold else ('georgiaz.ttf' if italic else 'georgia.ttf')
    
    candidates = [
        os.path.join(os.path.dirname(__file__), 'static', 'fonts', f_name),
        os.path.join('static', 'fonts', f_name),
        os.path.join('public', 'static', 'fonts', f_name),
        os.path.join('C:', os.sep, 'Windows', 'Fonts', f_name)
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()

def load_image(path):
    """
    Safely load an illustration or cover image from:
    1. Cloudinary or remote HTTP/HTTPS URL
    2. Local static filesystem directories
    Returns a PIL Image in RGB mode, or None on failure.
    """
    if not path:
        return None
    try:
        path_str = str(path).strip()
        if path_str.startswith('http://') or path_str.startswith('https://') or path_str.startswith('//'):
            url = 'https:' + path_str if path_str.startswith('//') else path_str
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = resp.read()
                return Image.open(io.BytesIO(data)).convert('RGB')
        
        # Local static folders
        base_dir = os.path.dirname(__file__)
        for folder in ['static', 'public/static']:
            full_path = os.path.join(base_dir, folder, path_str)
            if os.path.exists(full_path):
                return Image.open(full_path).convert('RGB')
            # Also check direct path
            if os.path.exists(path_str):
                return Image.open(path_str).convert('RGB')
    except Exception as e:
        print(f"[PDF Generator] Note: could not load image {path}: {e}")
    return None

def sanitize_text(text):
    """Strip HTML markup and unescape HTML entities for clean typography."""
    if not text:
        return ''
    # Replace <br> with newline
    t = re.sub(r'<br\s*/?>', '\n', str(text), flags=re.IGNORECASE)
    # Strip remaining HTML tags
    t = re.sub(r'<[^>]+>', ' ', t)
    # Unescape HTML entities
    t = html.unescape(t)
    return t.strip()

def wrap_text(text, font, max_width, draw):
    """Wrap plain text into balanced lines that fit within max_width."""
    lines = []
    clean = sanitize_text(text)
    for paragraph in clean.split('\n'):
        p = paragraph.strip()
        if not p:
            lines.append('')
            continue
        words = p.split(' ')
        current_line = []
        for word in words:
            if not word:
                continue
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_w = bbox[2] - bbox[0]
            if line_w <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
    return lines

def create_page_base():
    """Create a warm ivory storybook paper sheet with double golden border."""
    img = Image.new('RGB', (PAGE_W, PAGE_H), (252, 250, 246))
    d = ImageDraw.Draw(img)
    # Outer storybook rule frame
    d.rectangle([(26, 26), (PAGE_W - 26, PAGE_H - 26)], outline=(222, 212, 196), width=2)
    # Inner delicate rule frame
    d.rectangle([(32, 32), (PAGE_W - 32, PAGE_H - 32)], outline=(238, 230, 218), width=1)
    # Corner flourishes
    for cx, cy in [(32, 32), (PAGE_W - 32, 32), (32, PAGE_H - 32), (PAGE_W - 32, PAGE_H - 32)]:
        d.ellipse([(cx - 3, cy - 3), (cx + 3, cy + 3)], fill=(205, 190, 168))
    return img, d

def generate_storybook_pdf(book, spreads):
    """
    Generate a complete, professionally formatted multi-page storybook PDF.
    
    Structure:
    - Page 1: Front Cover with original cover image, title, author and logo.
    - Pages 2..N: Sequential story spreads (Left = Scene Illustration, Right = Story Prose).
    - Final page concludes with '★ The End ★' and ending message.
    
    Returns raw PDF bytes.
    """
    pages = []

    # -------------------------------------------------------------------------
    # 1. FRONT COVER PAGE
    # -------------------------------------------------------------------------
    cover_img, d_cov = create_page_base()
    
    # Ornamental Header
    f_ornament = get_font(15)
    d_cov.text((PAGE_W // 2, 60), '✦   A   L I T T L E   S T O R Y B O O K   ✦', fill=(145, 120, 90), font=f_ornament, anchor='mm')
    
    # Book Title
    f_cov_title = get_font(34, bold=True)
    title_text = book.get('title', 'Enchanted Storybook')
    d_cov.text((PAGE_W // 2, 105), title_text, fill=(45, 30, 65), font=f_cov_title, anchor='mm')
    
    # Book Subtitle / Category
    f_cov_sub = get_font(16, italic=True)
    category_text = book.get('category') or 'A Cozy Bedtime Story'
    d_cov.text((PAGE_W // 2, 142), f"{category_text} • Little Bedtime Tales", fill=(110, 95, 125), font=f_cov_sub, anchor='mm')
    
    # Cover Artwork
    cov_art = load_image(book.get('cover'))
    if cov_art:
        box_w, box_h = 660, 620
        art_w, art_h = cov_art.size
        ratio = min(box_w / art_w, box_h / art_h)
        new_w, new_h = max(1, int(art_w * ratio)), max(1, int(art_h * ratio))
        cov_resized = cov_art.resize((new_w, new_h), Image.Resampling.LANCZOS)
        pos_x = (PAGE_W - new_w) // 2
        pos_y = 175 + (box_h - new_h) // 2
        # Frame
        d_cov.rectangle([(pos_x - 3, pos_y - 3), (pos_x + new_w + 3, pos_y + new_h + 3)], outline=(215, 202, 185), width=2)
        cover_img.paste(cov_resized, (pos_x, pos_y))
    else:
        # Fallback decorative cover box
        d_cov.rectangle([(100, 220), (700, 780)], fill=(245, 240, 232), outline=(215, 202, 185), width=2)
        d_cov.text((PAGE_W // 2, 500), '✨ 📖 ✨', fill=(160, 140, 110), font=get_font(28), anchor='mm')

    # Cover Footer
    author_name = book.get('author') or 'Once Upon a Page'
    d_cov.text((PAGE_W // 2, 920), f"Written with love by {author_name}", fill=(80, 65, 95), font=get_font(16), anchor='mm')
    d_cov.text((PAGE_W // 2, 955), 'Once Upon a Page ✨', fill=(140, 125, 155), font=get_font(14, bold=True), anchor='mm')
    pages.append(cover_img)

    # -------------------------------------------------------------------------
    # 2. STORY SPREADS (Left Illustration + Right Typography)
    # -------------------------------------------------------------------------
    total_spreads = len(spreads)
    for idx, sp in enumerate(spreads, start=1):
        left_num = sp.get('page_num_left') or ((idx * 2) - 1)
        right_num = sp.get('page_num_right') or (idx * 2)
        chapter_title = sp.get('title') or f"Chapter {idx}"
        
        # --- LEFT PAGE: SCENE ILLUSTRATION ---
        p_left, d_left = create_page_base()
        
        # Chapter banner at top
        d_left.text((PAGE_W // 2, 55), f"Chapter {idx} • {chapter_title}", fill=(120, 105, 135), font=get_font(15, bold=True), anchor='mm')
        
        # Scene illustration image
        scene_art = load_image(sp.get('illustration')) or cov_art
        if scene_art:
            box_w, box_h = 680, 780
            art_w, art_h = scene_art.size
            ratio = min(box_w / art_w, box_h / art_h)
            new_w, new_h = max(1, int(art_w * ratio)), max(1, int(art_h * ratio))
            scene_resized = scene_art.resize((new_w, new_h), Image.Resampling.LANCZOS)
            pos_x = (PAGE_W - new_w) // 2
            pos_y = 85 + (box_h - new_h) // 2
            d_left.rectangle([(pos_x - 2, pos_y - 2), (pos_x + new_w + 2, pos_y + new_h + 2)], outline=(220, 208, 192), width=2)
            p_left.paste(scene_resized, (pos_x, pos_y))
        
        # Left footer
        d_left.text((50, PAGE_H - 48), f"Chapter {idx}", fill=(155, 145, 165), font=get_font(13), anchor='ls')
        d_left.text((PAGE_W - 50, PAGE_H - 48), str(left_num), fill=(130, 115, 140), font=get_font(14, bold=True), anchor='rs')
        pages.append(p_left)

        # --- RIGHT PAGE: STORY TEXT & TYPOGRAPHY ---
        p_right, d_right = create_page_base()
        
        # Chapter header & ornament
        d_right.text((PAGE_W // 2, 85), '✦   ❧   ✦', fill=(185, 155, 105), font=get_font(18), anchor='mm')
        d_right.text((PAGE_W // 2, 130), chapter_title, fill=(45, 30, 65), font=get_font(26, bold=True), anchor='mm')
        d_right.line([(PAGE_W // 2 - 90, 162), (PAGE_W // 2 + 90, 162)], fill=(225, 215, 195), width=1)
        
        # Story body text
        f_body = get_font(20)
        body_lines = wrap_text(sp.get('text', ''), f_body, 640, d_right)
        cur_y = 210
        for line in body_lines:
            if line == '':
                cur_y += 18
                continue
            d_right.text((PAGE_W // 2, cur_y), line, fill=(45, 35, 60), font=f_body, anchor='mm')
            cur_y += 34
        
        # Dialogue quote (if present)
        if sp.get('dialogue'):
            cur_y += 24
            f_diag = get_font(19, italic=True)
            diag_text = sanitize_text(sp.get('dialogue'))
            d_lines = wrap_text(f'"{diag_text}"', f_diag, 580, d_right)
            for dl in d_lines:
                d_right.text((PAGE_W // 2, cur_y), dl, fill=(85, 45, 105), font=f_diag, anchor='mm')
                cur_y += 30

        # Moral / Final message card (if present)
        if sp.get('final_message'):
            cur_y += 30
            card_w, card_h = 620, 120
            card_x = (PAGE_W - card_w) // 2
            d_right.rectangle([(card_x, cur_y), (card_x + card_w, cur_y + card_h)], fill=(255, 248, 235), outline=(235, 215, 175), width=2)
            d_right.text((PAGE_W // 2, cur_y + 30), '💛', font=get_font(20), anchor='mm')
            f_moral = get_font(17, italic=True)
            m_lines = wrap_text(sp.get('final_message'), f_moral, 560, d_right)
            m_y = cur_y + 65
            for ml in m_lines:
                d_right.text((PAGE_W // 2, m_y), ml, fill=(75, 45, 95), font=f_moral, anchor='mm')
                m_y += 24
            cur_y += card_h + 10

        # Final Spread: 'The End' ribbon; Intermediate Spreads: celestial divider
        if idx == total_spreads:
            d_right.text((PAGE_W // 2, 850), '★   T H E   E N D   ★', fill=(155, 115, 65), font=get_font(20, bold=True), anchor='mm')
            d_right.text((PAGE_W // 2, 885), '✦  Every little story holds a little magic  ✦', fill=(155, 140, 170), font=get_font(14, italic=True), anchor='mm')
        else:
            d_right.text((PAGE_W // 2, 860), '⭐   ⋆   ✦   ⋆   ⭐', fill=(195, 175, 130), font=get_font(16), anchor='mm')

        # Right footer
        d_right.text((50, PAGE_H - 48), 'Once Upon a Page', fill=(155, 145, 165), font=get_font(13), anchor='ls')
        d_right.text((PAGE_W - 50, PAGE_H - 48), str(right_num), fill=(130, 115, 140), font=get_font(14, bold=True), anchor='rs')
        pages.append(p_right)

    # -------------------------------------------------------------------------
    # 3. SAVE AS MULTI-PAGE PDF
    # -------------------------------------------------------------------------
    out_buf = io.BytesIO()
    if pages:
        pages[0].save(out_buf, format='PDF', save_all=True, append_images=pages[1:], resolution=150.0)
    return out_buf.getvalue()
