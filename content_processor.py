import os
import json
import re
import random
import google.generativeai as genai

def verify_api_key(api_key):
    """
    Verifies if the provided Gemini API key is valid and finds a working model.
    """
    try:
        genai.configure(api_key=api_key)
        # Try models in order of preference (Updated December 2, 2025)
        models_to_try = ['gemini-3-pro-preview', 'gemini-2.5-pro', 'gemini-2.5-flash']
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                model.generate_content("Test")
                return True, f"Success! Using {model_name}"
            except:
                continue
                
        return False, "Key valid but no supported models found."
    except Exception as e:
        return False, str(e)

def get_layout_for_slide(slide_index, total_slides, content_type, seed=0):
    """
    Deterministically selects a layout based on slide position and seed.
    """
    random.seed(seed + slide_index)
    
    if slide_index == 0:
        return "layout-cover"
    elif slide_index == total_slides - 1:
        return "layout-cta"
    
    # Middle slides
    options = ["layout-list", "layout-quote", "layout-data", "layout-split"]
    
    # Weight options based on content type (heuristic)
    if content_type == "Data Insights":
        options.extend(["layout-data"] * 3)
    elif content_type == "Tutorial":
        options.extend(["layout-list", "layout-split"] * 2)
        
    return random.choice(options)

def process_content(text, api_key=None, provider="gemini", content_type="Success Story", style_seed=42):
    """
    Analyzes the transcript using an LLM to generate structured carousel content.
    Returns a list of slide objects with layout information.
    """
    if not text:
        return [], "No text provided"

    error_msg = None
    
    if api_key:
        try:
            if provider == "gemini":
                genai.configure(api_key=api_key)
                
                # Define content-type-specific prompts
                prompts = {
                    "Success Story": "Focus on problem-solution-result narrative. Use data where possible.",
                    "Tutorial": "Break down into clear, actionable steps. Use 'Split' or 'List' layouts.",
                    "Tips & Tricks": "Quick, punchy tips. Use 'Quote' or 'List' layouts.",
                    "Data Insights": "Focus on statistics and trends. Use 'Data' layouts."
                }
                
                type_instructions = prompts.get(content_type, prompts["Success Story"])
                
                system_prompt = f"""
                You are an expert Social Media Designer and Copywriter. 
                Transform the provided text into a high-performing 5-8 slide LinkedIn carousel.
                
                **Goal:** Create a "{content_type}" carousel.
                {type_instructions}
                
                **Available Layouts:**
                - `layout-cover`: Big bold title, minimal text. (Slide 1)
                - `layout-quote`: A powerful quote or statement.
                - `layout-list`: 3-5 bullet points.
                - `layout-data`: Key statistic or chart data.
                - `layout-split`: Image/Icon on one side, text on the other.
                - `layout-cta`: Call to Action. (Last Slide)
                
                **Output JSON format ONLY:**
                [
                    {{
                        "layout": "layout-cover",
                        "title": "Main Headline",
                        "subtitle": "Compelling Subhead",
                        "body": "Brief intro or hook.",
                        "image_prompt": "Description for an illustration"
                    }},
                    {{
                        "layout": "layout-list",
                        "title": "Key Point 1",
                        "body": ["Bullet 1", "Bullet 2", "Bullet 3"],
                        "image_prompt": "Icon representing X"
                    }},
                    ...
                ]
                
                **Rules:**
                1. Vary the layouts. Don't use the same layout twice in a row (except List).
                2. Keep text concise. No walls of text.
                3. Ensure the flow is logical.
                4. Extract specific stats for 'layout-data'.
                """
                
                final_prompt = f"""
                {system_prompt}
                
                **Input Text:**
                {text[:20000]}
                """
                
                # Try models in sequence (Updated December 2, 2025)
                models_to_try = ['gemini-3-pro-preview', 'gemini-2.5-pro', 'gemini-2.5-flash']
                last_exception = None
                
                for model_name in models_to_try:
                    try:
                        # print(f"Trying model: {model_name}...")
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(final_prompt)
                        content = response.text
                        
                        # Robust JSON Extraction
                        start_idx = content.find('[')
                        end_idx = content.rfind(']')
                        
                        if start_idx != -1 and end_idx != -1:
                            json_str = content[start_idx:end_idx+1]
                            slides = json.loads(json_str)
                            
                            # Post-processing: Ensure layouts are valid and add variety if needed
                            for i, slide in enumerate(slides):
                                if "layout" not in slide or slide["layout"] not in ["layout-cover", "layout-quote", "layout-list", "layout-data", "layout-split", "layout-cta"]:
                                    slide["layout"] = get_layout_for_slide(i, len(slides), content_type, style_seed)
                                
                                # Ensure body is a list for list layouts
                                if slide["layout"] == "layout-list" and isinstance(slide.get("body"), str):
                                    slide["body"] = [slide["body"]]
                                    
                            return slides, None
                        else:
                            raise ValueError("No JSON array found")
                            
                    except Exception as e:
                        # print(f"Model {model_name} failed: {e}")
                        last_exception = e
                        continue
                
                if last_exception:
                    raise last_exception
                    
        except Exception as e:
            error_msg = f"AI generation failed: {str(e)}"
            print(f"{error_msg}. Falling back to heuristic.")
    
    # Fallback Heuristic (Updated for new structure)
    # This is a basic fallback if AI fails or no key is provided
    random.seed(style_seed)
    
    fallback_slides = [
        {
            "layout": "layout-cover",
            "title": "Transform Your Business",
            "subtitle": "Success Story",
            "body": "How we achieved X with Y."
        },
        {
            "layout": "layout-split",
            "title": "The Challenge",
            "subtitle": "What was wrong",
            "body": "Manual processes were slowing us down."
        },
        {
            "layout": "layout-list",
            "title": "The Solution",
            "body": ["Implemented Automation", "Streamlined Workflows", "Real-time Data"]
        },
        {
            "layout": "layout-data",
            "title": "The Results",
            "subtitle": "Measurable Impact",
            "stats": [{"value": "50%", "label": "Growth"}, {"value": "2x", "label": "Speed"}]
        },
        {
            "layout": "layout-cta",
            "title": "Ready to Scale?",
            "subtitle": "Contact Us Today",
            "body": "Link in bio"
        }
    ]
    
    return fallback_slides, error_msg

