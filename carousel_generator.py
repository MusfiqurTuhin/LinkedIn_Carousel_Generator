import os
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter

class CarouselGenerator:
    def __init__(self, logo_path, brand_color=None):
        self.width = 1080
        self.height = 1080
        self.logo_path = logo_path
        
        # Premium Color Palette (Odoo/Metamorphosis inspired but refined)
        self.primary_color = brand_color if brand_color else "#714B67" # Deep Purple
        self.secondary_color = "#017E84" # Teal
        self.accent_color = "#F0F4F7" # Light Grey/Blue
        self.text_color = "#1A1A1A" # Almost Black
        self.white = "#FFFFFF"
        
        # Load Logo
        self.logo = None
        if logo_path and os.path.exists(logo_path):
            try:
                self.logo = Image.open(logo_path).convert("RGBA")
                # Resize logic
                base_width = 250
                w_percent = (base_width / float(self.logo.size[0]))
                h_size = int((float(self.logo.size[1]) * float(w_percent)))
                self.logo = self.logo.resize((base_width, h_size), Image.Resampling.LANCZOS)
            except Exception as e:
                print(f"Error loading logo: {e}")

        # Load Premium Fonts (Inter)
        self.load_fonts()

    def load_fonts(self):
        # Helper to download font if not exists
        font_url = "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Bold.otf"
        font_path = "Inter-Bold.otf"
        if not os.path.exists(font_path):
            try:
                r = requests.get(font_url)
                with open(font_path, 'wb') as f:
                    f.write(r.content)
            except:
                pass
        
        try:
            self.font_title = ImageFont.truetype("Inter-Bold.otf", 90)
            self.font_subtitle = ImageFont.truetype("Inter-Bold.otf", 50)
            self.font_body = ImageFont.truetype("Inter-Bold.otf", 45) # Using bold for readability or standard if available
            self.font_footer = ImageFont.truetype("Inter-Bold.otf", 30)
        except:
            self.font_title = ImageFont.load_default()
            self.font_subtitle = ImageFont.load_default()
            self.font_body = ImageFont.load_default()
            self.font_footer = ImageFont.load_default()

    def create_gradient_bg(self):
        # Create a premium soft gradient background
        base = Image.new('RGB', (self.width, self.height), self.white)
        draw = ImageDraw.Draw(base)
        
        # Draw some soft blobs for "depth"
        # Blob 1 (Top Right - Primary)
        draw.ellipse([800, -200, 1300, 300], fill=self.primary_color)
        # Blob 2 (Bottom Left - Secondary)
        draw.ellipse([-200, 800, 300, 1300], fill=self.secondary_color)
        
        # Blur heavily to create gradient mesh effect
        base = base.filter(ImageFilter.GaussianBlur(radius=100))
        
        # Overlay a white layer with opacity to lighten it up
        overlay = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 230))
        base.paste(overlay, (0,0), overlay)
        
        return base

    def draw_text_wrapped(self, draw, text, font, max_width, start_y, color, line_spacing=15):
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
        for line in lines:
            draw.text((80, y), line, font=font, fill=color)
            bbox = draw.textbbox((0, 0), line, font=font)
            y += (bbox[3] - bbox[1]) + line_spacing
        return y

    def generate_slide(self, slide_data, page_num, total_pages, output_dir):
        img = self.create_gradient_bg()
        draw = ImageDraw.Draw(img)

        # Header: Logo
        if self.logo:
            img.paste(self.logo, (80, 80), self.logo)

        # Header: Page Indicator (Pill shape)
        pill_w, pill_h = 120, 50
        pill_x, pill_y = self.width - 80 - pill_w, 80
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=25, fill="#E0E0E0")
        draw.text((pill_x + 25, pill_y + 10), f"{page_num}/{total_pages}", font=self.font_footer, fill="#555")

        # Content
        current_y = 300
        
        # Subtitle (Tagline)
        if 'subtitle' in slide_data:
            draw.text((80, current_y), slide_data['subtitle'].upper(), font=self.font_subtitle, fill=self.secondary_color)
            current_y += 70

        # Title
        if 'title' in slide_data:
            current_y = self.draw_text_wrapped(draw, slide_data['title'], self.font_title, 920, current_y, self.primary_color, line_spacing=20)
            current_y += 50

        # Divider
        draw.line([(80, current_y), (200, current_y)], fill=self.secondary_color, width=5)
        current_y += 60

        # Body
        if 'body' in slide_data:
            if isinstance(slide_data['body'], list):
                for item in slide_data['body']:
                    # Custom bullet
                    draw.ellipse([80, current_y + 15, 95, current_y + 30], fill=self.secondary_color)
                    self.draw_text_wrapped(draw, item, self.font_body, 880, current_y, self.text_color) 
                    # Approximate height increment since draw_text_wrapped returns new Y but we need to handle list spacing
                    # Ideally draw_text_wrapped should return the new Y.
                    # Let's just add a fixed amount for now or recalculate.
                    # Re-calculating for simplicity of this snippet:
                    bbox = draw.textbbox((0, 0), item, font=self.font_body) # Rough estimate of single line
                    # For multi-line bullets, this needs the return value. 
                    # My draw_text_wrapped returns y, so let's use it.
                    # But I need to call it with offset x for text.
                    # Let's redo draw_text_wrapped call for list item
                    
                    # Indented text
                    lines = []
                    words = item.split()
                    current_line = []
                    for word in words:
                        test_line = ' '.join(current_line + [word])
                        bbox = draw.textbbox((0, 0), test_line, font=self.font_body)
                        if bbox[2] - bbox[0] <= 850: # Width adjusted for indent
                            current_line.append(word)
                        else:
                            lines.append(' '.join(current_line))
                            current_line = [word]
                    lines.append(' '.join(current_line))
                    
                    temp_y = current_y
                    for line in lines:
                        draw.text((110, temp_y), line, font=self.font_body, fill=self.text_color)
                        bbox = draw.textbbox((0, 0), line, font=self.font_body)
                        temp_y += (bbox[3] - bbox[1]) + 15
                    
                    current_y = temp_y + 30 # Spacing between bullets
            else:
                current_y = self.draw_text_wrapped(draw, slide_data['body'], self.font_body, 920, current_y, self.text_color)

        # Footer
        draw.line([(0, self.height - 120), (self.width, self.height - 120)], fill="#EEEEEE", width=2)
        draw.text((80, self.height - 80), "metamorphosis.com.bd", font=self.font_footer, fill="#888")
        
        # Progress Bar at bottom
        progress_width = (self.width / total_pages) * page_num
        draw.rectangle([0, self.height - 15, progress_width, self.height], fill=self.primary_color)

        # Save
        filename = f"slide_{page_num}.png"
        img.save(os.path.join(output_dir, filename))
        return os.path.join(output_dir, filename)
