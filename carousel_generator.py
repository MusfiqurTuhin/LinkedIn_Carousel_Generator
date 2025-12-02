import os
import base64
from jinja2 import Environment, FileSystemLoader
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

class CarouselGenerator:
    def __init__(self, logo_path, brand_color=None, secondary_color=None, font_name="Inter", author_handle="@metamorphosis"):
        self.logo_path = logo_path
        self.primary_color = brand_color if brand_color else "#714B67"
        self.secondary_color = secondary_color if secondary_color else "#017E84"
        self.font_name = font_name
        self.author_handle = author_handle
        
        # Setup Jinja2
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.template = self.env.get_template('carousel_template.html')

    def get_logo_base64(self):
        if self.logo_path and os.path.exists(self.logo_path):
            with open(self.logo_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        return None

    def generate_all_slides(self, slides_content, output_dir):
        """
        Generates all slides at once by rendering a single HTML with all slides,
        then taking screenshots of each slide element.
        """
        # 1. Render HTML
        logo_b64 = self.get_logo_base64()
        html_content = self.template.render(
            slides=slides_content,
            primary_color=self.primary_color,
            secondary_color=self.secondary_color,
            font_name=self.font_name,
            author_handle=self.author_handle,
            logo_base64=logo_b64
        )
        
        temp_html_path = os.path.abspath(os.path.join(output_dir, "temp_carousel.html"))
        with open(temp_html_path, "w") as f:
            f.write(html_content)
            
        # 2. Setup Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        # Set window size large enough to fit the slide (1080x1080)
        chrome_options.add_argument("--window-size=1200,1200")
        
        driver = None
        generated_files = []
        
        try:
            # Try using webdriver_manager (local) or system driver (cloud)
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except:
                # Fallback for environments where driver is in PATH (like Streamlit Cloud sometimes)
                driver = webdriver.Chrome(options=chrome_options)

            # 3. Open File
            driver.get(f"file://{temp_html_path}")
            time.sleep(1) # Wait for fonts/render
            
            # 4. Screenshot each slide
            for i in range(len(slides_content)):
                slide_id = f"slide-{i+1}"
                try:
                    element = driver.find_element(By.ID, slide_id)
                    output_path = os.path.join(output_dir, f"slide_{i+1}.png")
                    element.screenshot(output_path)
                    generated_files.append(output_path)
                except Exception as e:
                    print(f"Error capturing slide {i+1}: {e}")

        except Exception as e:
            print(f"Selenium Error: {e}")
            raise e
        finally:
            if driver:
                driver.quit()
            # Cleanup temp file
            # os.remove(temp_html_path) 
            
        return generated_files

    # Compatibility method for existing code (though we prefer batch generation now)
    def generate_slide(self, slide_data, page_num, total_pages, output_dir):
        # This method signature was used by the loop in app.py.
        # Since we now generate ALL slides in one go for efficiency (one browser session),
        # we should refactor app.py to call generate_all_slides.
        # For now, this is a placeholder or we can implement single slide generation if needed.
        pass
