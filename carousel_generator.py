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
    def __init__(self, logo_path, brand_color=None, secondary_color=None, font_name="Inter", author_handle="@metamorphosis", brand_name="Metamorphosis"):
        self.logo_path = logo_path
        self.primary_color = brand_color if brand_color else "#714B67"
        self.secondary_color = secondary_color if secondary_color else "#017E84"
        self.font_name = font_name
        self.author_handle = author_handle
        self.brand_name = brand_name
        
        # Setup Jinja2
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.template = self.env.get_template('carousel_template.html')

    def get_logo_base64(self):
        if self.logo_path and os.path.exists(self.logo_path):
            with open(self.logo_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        return None

    def get_image_base64_from_url(self, url):
        if not url:
            return None
        try:
            import requests
            response = requests.get(url)
            if response.status_code == 200:
                return base64.b64encode(response.content).decode('utf-8')
        except Exception as e:
            print(f"Failed to download image: {e}")
        return None

    def generate_html_only(self, slides_content, bg_image_url=None, bg_opacity=0.15, bg_mode="Solid Color"):
        """
        Generates the HTML content for the carousel without taking screenshots.
        Useful for live preview.
        """
        logo_b64 = self.get_logo_base64()
        
        # Handle local file paths vs URLs for background
        bg_image_b64 = None
        if bg_image_url:
            if os.path.exists(bg_image_url):
                # Local file
                with open(bg_image_url, "rb") as img_file:
                    bg_image_b64 = base64.b64encode(img_file.read()).decode('utf-8')
            else:
                # URL
                bg_image_b64 = self.get_image_base64_from_url(bg_image_url)
        
        html_content = self.template.render(
            slides=slides_content,
            primary_color=self.primary_color,
            secondary_color=self.secondary_color,
            bg_color="#FFFFFF", # Default white bg for slides
            text_color="#333333", # Default dark text
            font_name=self.font_name,
            author_handle=self.author_handle,
            brand_name=self.brand_name,
            logo_base64=logo_b64,
            bg_image_base64=bg_image_b64,
            bg_opacity=bg_opacity,
            bg_mode=bg_mode
        )
        
        return html_content

    def generate_all_slides(self, slides_content, output_dir, bg_image_url=None, bg_opacity=0.15, bg_mode="Solid Color"):
        """
        Generates all slides at once by rendering a single HTML with all slides,
        then taking screenshots of each slide element.
        """
        # 1. Render HTML
        html_content = self.generate_html_only(slides_content, bg_image_url, bg_opacity, bg_mode)
        
        temp_html_path = os.path.abspath(os.path.join(output_dir, "temp_carousel.html"))
        with open(temp_html_path, "w") as f:
            f.write(html_content)
            
        # 2. Setup Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--hide-scrollbars")
        # High DPI rendering for better quality
        chrome_options.add_argument("--force-device-scale-factor=2")
        # Set window size large enough to fit the slide (1080x1080)
        chrome_options.add_argument("--window-size=2000,2000")
        # Performance optimizations
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.page_load_strategy = 'eager'
        
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
            # Wait for fonts/render (Increased for safety)
            time.sleep(2.0) 

            
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
