import os
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter

class CarouselGenerator:
    def __init__(self, logo_path, brand_color=None):
        self.width = 1080
        self.height = 1080
        self.logo_path = logo_path
        
        # Exact Colors from HTML
        self.primary_color = brand_color if brand_color else "#714B67" # Odoo Purple
        self.secondary_color = "#017E84" # Odoo Teal
        self.text_color = "#333333"
        self.white = "#FFFFFF"
        self.grey_text = "#888888"
        self.bg_overlay_start = (113, 75, 103, 13) # 5% opacity
        self.bg_overlay_end = (1, 126, 132, 13)   # 5% opacity
        
        # Load Logo
        self.logo = None
        if logo_path and os.path.exists(logo_path):
            try:
                self.logo = Image.open(logo_path).convert("RGBA")
                # Resize logic - Height 50px as per HTML
                h_size = 50
                w_percent = (h_size / float(self.logo.size[1]))
                w_size = int((float(self.logo.size[0]) * float(w_percent)))
                self.logo = self.logo.resize((w_size, h_size), Image.Resampling.LANCZOS)
            except Exception as e:
                print(f"Error loading logo: {e}")

        # Load Fonts (Inter)
        self.load_fonts()

    def load_fonts(self):
        # Helper to download font if not exists
        font_url_bold = "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Bold.otf"
        font_url_reg = "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Regular.otf"
        
        if not os.path.exists("Inter-Bold.otf"):
            try:
                r = requests.get(font_url_bold)
                with open("Inter-Bold.otf", 'wb') as f: f.write(r.content)
            except: pass
        if not os.path.exists("Inter-Regular.otf"):
            try:
                r = requests.get(font_url_reg)
                with open("Inter-Regular.otf", 'wb') as f: f.write(r.content)
            except: pass
        
        try:
            # Sizes from HTML
            self.font_h1 = ImageFont.truetype("Inter-Bold.otf", 72)
            self.font_h2 = ImageFont.truetype("Inter-Bold.otf", 48) # Using Bold for subtitle to pop
            self.font_body = ImageFont.truetype("Inter-Regular.otf", 32)
            self.font_footer = ImageFont.truetype("Inter-Regular.otf", 24)
            self.font_stat_num = ImageFont.truetype("Inter-Bold.otf", 64)
            self.font_stat_label = ImageFont.truetype("Inter-Regular.otf", 28)
            self.font_cta = ImageFont.truetype("Inter-Bold.otf", 32)
        except:
            self.font_h1 = ImageFont.load_default()
            self.font_h2 = ImageFont.load_default()
            self.font_body = ImageFont.load_default()
            self.font_footer = ImageFont.load_default()
            self.font_stat_num = ImageFont.load_default()
            self.font_stat_label = ImageFont.load_default()
            self.font_cta = ImageFont.load_default()

    def create_bg(self):
        # White background
        base = Image.new('RGB', (self.width, self.height), self.white)
        draw = ImageDraw.Draw(base, 'RGBA')
        
        # Subtle Gradient Overlay (Top Left to Bottom Right)
        # Simulating linear-gradient(135deg, rgba(113, 75, 103, 0.05) 0%, rgba(1, 126, 132, 0.05) 100%)
        # Since Pillow doesn't do complex gradients easily, we'll do a simple interpolation
        # Or just a very subtle wash. Let's do a solid very light wash for simplicity and performance
        # or a pre-rendered gradient.
        # Let's draw a rectangle with the average color at 5% opacity
        draw.rectangle([0, 0, self.width, self.height], fill=(57, 100, 117, 13)) 
        
        return base

    def draw_text_wrapped(self, draw, text, font, max_width, start_y, color, line_spacing=1.5):
        lines = []
        words = text.split()
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))

        y = start_y
        # Calculate line height based on font size * spacing
        # font.size is not always available, use bbox of "A"
        bbox_a = draw.textbbox((0, 0), "A", font=font)
        line_height = (bbox_a[3] - bbox_a[1]) * line_spacing

        for line in lines:
            draw.text((80, y), line, font=font, fill=color)
            y += line_height
        return y

    def draw_stat_box(self, draw, number, label, x, y, width):
        # Shadow/Box effect is hard in pure PIL without blurring.
        # We will draw a simple bordered box with the left accent.
        
        box_h = 180
        # Background
        draw.rectangle([x, y, x + width, y + box_h], fill="#F9F9F9") # Slightly off-white to stand out
        # Left Border
        draw.rectangle([x, y, x + 10, y + box_h], fill=self.secondary_color)
        
        # Text
        draw.text((x + 40, y + 30), number, font=self.font_stat_num, fill=self.primary_color)
        draw.text((x + 40, y + 110), label, font=self.font_stat_label, fill="#555555")
        
        return y + box_h + 30

    def generate_slide(self, slide_data, page_num, total_pages, output_dir):
        img = self.create_bg()
        draw = ImageDraw.Draw(img)

        # --- Header (Padding 60px) ---
        # Logo
        if self.logo:
            img.paste(self.logo, (60, 60), self.logo)
        else:
            # Text placeholder if no logo
            draw.text((60, 60), "Metamorphosis", font=self.font_footer, fill=self.primary_color) # Using footer font as fallback

        # Page Number
        page_text = f"{page_num:02d}/{total_pages:02d}"
        bbox = draw.textbbox((0, 0), page_text, font=self.font_footer)
        p_w = bbox[2] - bbox[0]
        draw.text((self.width - 60 - p_w, 60), page_text, font=self.font_footer, fill=self.grey_text)

        # --- Content (Padding 80px horizontal, Centered Vertical) ---
        # We need to calculate total height first to center it, but that's complex with wrapping.
        # We'll start at a fixed top offset (e.g., 250px) which usually looks good.
        current_y = 250
        
        # Subtitle (H2) - Secondary Color
        if 'subtitle' in slide_data:
            draw.text((80, current_y), slide_data['subtitle'], font=self.font_h2, fill=self.secondary_color)
            current_y += 80 # Margin bottom 40px + height approx

        # Title (H1) - Primary Color
        if 'title' in slide_data:
            current_y = self.draw_text_wrapped(draw, slide_data['title'], self.font_h1, 920, current_y, self.primary_color, line_spacing=1.2)
            current_y += 50 # Margin bottom 30px

        # Body (P or List)
        if 'body' in slide_data:
            body_content = slide_data['body']
            
            # Check if it's a list or looks like stats
            if isinstance(body_content, list):
                # Check if it looks like stats (short numbers?)
                # For now, treat as bullet points
                for item in body_content:
                    # Custom Bullet
                    draw.text((80, current_y), "•", font=self.font_h2, fill=self.secondary_color) # Bullet
                    # Indent text
                    # We need a custom wrap that indents
                    lines = []
                    words = item.split()
                    current_line = []
                    for word in words:
                        test_line = ' '.join(current_line + [word])
                        bbox = draw.textbbox((0, 0), test_line, font=self.font_body)
                        if bbox[2] - bbox[0] <= 880: # 920 - 40px indent
                            current_line.append(word)
                        else:
                            lines.append(' '.join(current_line))
                            current_line = [word]
                    lines.append(' '.join(current_line))

                    # Draw lines
                    bbox_a = draw.textbbox((0, 0), "A", font=self.font_body)
                    line_height = (bbox_a[3] - bbox_a[1]) * 1.5
                    
                    temp_y = current_y + 10 # Align with bullet
                    for line in lines:
                        draw.text((120, temp_y), line, font=self.font_body, fill=self.text_color)
                        temp_y += line_height
                    
                    current_y = temp_y + 20 # Margin between items
            else:
                # Regular paragraph
                current_y = self.draw_text_wrapped(draw, body_content, self.font_body, 920, current_y, self.text_color)

        # --- Footer (Padding 60px) ---
        # Border Top
        draw.line([(60, self.height - 100), (self.width - 60, self.height - 100)], fill="#E0E0E0", width=1)
        
        # Website
        draw.text((60, self.height - 80), "metamorphosis.com.bd", font=self.font_footer, fill=self.grey_text)
        
        # Swipe Text
        swipe_text = "Swipe →"
        if page_num == total_pages:
            swipe_text = "Link in bio"
        
        bbox = draw.textbbox((0, 0), swipe_text, font=self.font_footer)
        s_w = bbox[2] - bbox[0]
        draw.text((self.width - 60 - s_w, self.height - 80), swipe_text, font=self.font_footer, fill=self.grey_text)

        # Save
        filename = f"slide_{page_num}.png"
        img.save(os.path.join(output_dir, filename))
        return os.path.join(output_dir, filename)
