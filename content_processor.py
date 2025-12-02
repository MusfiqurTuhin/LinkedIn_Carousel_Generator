import os
import json
import re
import google.generativeai as genai

def verify_api_key(api_key):
    """
    Verifies if the provided Gemini API key is valid and finds a working model.
    """
    try:
        genai.configure(api_key=api_key)
        # Try models in order of preference (Updated for 2025)
        models_to_try = ['gemini-2.0-flash-exp', 'gemini-1.5-pro', 'gemini-1.5-flash']
        
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

def process_content(text, api_key=None, provider="gemini", content_type="Success Story"):
    """
    Analyzes the transcript using an LLM to generate structured carousel content.
    Supports multiple content types with specialized prompts.
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
                    "Success Story": """
                **Structure (Success Story) - STRICTLY FOLLOW THIS:**
                
                **Slide 1: The Hook**
                - Title: The main achievement (e.g., "How [Company] Scaled Social Impact with Odoo").
                - Subtitle: "Success Story".
                - Body: "Powered by Metamorphosis - Bangladesh's Leading Odoo Partner" (or similar context).
                
                **Slide 2: The Challenge**
                - Title: "The Challenge".
                - Subtitle: Context (e.g., "[Company] faced critical bottlenecks:").
                - Body: A list of 3 specific pain points (e.g., "Manual processes", "Lack of data").
                
                **Slide 3: The Solution**
                - Title: "The Solution".
                - Subtitle: "Metamorphosis implemented a comprehensive Odoo ERP ecosystem:".
                - Body: A list of 3 specific solutions (e.g., "Automated Manufacturing", "Real-time Dashboards").
                
                **Slide 4: The Result**
                - Title: "The Result".
                - Subtitle: "Measurable Business Growth".
                - Body: LEAVE EMPTY.
                - Stats: Extract 2 key metrics. Format: [{"value": "45%", "label": "Business Growth"}, {"value": "50%", "label": "Faster Process"}].
                
                **Slide 5: CTA**
                - Title: "Ready to Transform Your Business?".
                - Subtitle: "Partner with the experts who deliver results.".
                - Body: "Contact Metamorphosis".
                """,
                    
                    "Tutorial": """
                **Structure (Tutorial) - STRICTLY FOLLOW THIS:**
                
                **Slide 1: Introduction**
                - Title: Main topic (e.g., "Master [Skill/Topic] in 5 Steps").
                - Subtitle: "Step-by-Step Guide".
                - Body: Brief intro about what they'll learn.
                
                **Slide 2-4: Steps**
                - Title: "Step [N]: [Action]" (e.g., "Step 1: Setup Your Environment").
                - Subtitle: Brief description.
                - Body: 2-3 bullet points with specific actions.
                
                **Slide 5: Conclusion**
                - Title: "You're Ready!".
                - Subtitle: "Key Takeaways".
                - Body: 2-3 summary points or next steps.
                """,
                    
                    "Tips & Tricks": """
                **Structure (Tips & Tricks) - STRICTLY FOLLOW THIS:**
                
                **Slide 1: Hook**
                - Title: Attention-grabbing statement (e.g., "10X Your Productivity").
                - Subtitle: "Pro Tips You Need to Know".
                - Body: Brief intro.
                
                **Slide 2-4: Tips**
                - Title: "Tip [N]: [Short Title]".
                - Subtitle: Category or context.
                - Body: 2-3 actionable bullet points.
                
                **Slide 5: Bonus**
                - Title: "Bonus Tip" or "Common Mistakes to Avoid".
                - Subtitle: Extra value.
                - Body: Final wisdom or CTA.
                """,
                    
                    "Data Insights": """
                **Structure (Data Insights) - STRICTLY FOLLOW THIS:**
                
                **Slide 1: Hook**
                - Title: Main insight (e.g., "The State of [Industry] in 2025").
                - Subtitle: "Data-Driven Insights".
                - Body: Brief context.
                
                **Slide 2-4: Key Stats**
                - Title: "[Stat Category]".
                - Subtitle: Context.
                - Stats: [{"value": "XXX", "label": "Description"}] - Use this format for visual impact.
                
                **Slide 5: Takeaway**
                - Title: "What This Means".
                - Subtitle: "Key Implications".
                - Body: 2-3 actionable insights.
                """
                }
                
                # Get the appropriate prompt structure
                type_instructions = prompts.get(content_type, prompts["Success Story"])
                
                # Base prompt
                base_prompt = f"""
                You are a Viral LinkedIn Content Creator. Transform the following content into a high-performing 5-slide carousel.
                
                Content:
                {text[:15000]}
                
                **Goal:** Create a {content_type} carousel.
                """
                
                final_prompt = f"""
                {base_prompt}
                {type_instructions}
                
                **Style Guide:**
                - Punchy, direct, no fluff.
                - Use emojis where appropriate.
                - Make it scannable and engaging.
                
                **Output JSON format ONLY:**
                [
                    {{
                        "title": "Slide Title", 
                        "subtitle": "Slide Subtitle", 
                        "body": "Body text or List of strings",
                        "stats": [{{"value": "45%", "label": "Growth"}}] // OPTIONAL: Only for Result/Stats slides
                    }},
                    ...
                ]
                """
                
                # Try models in sequence
                models_to_try = ['gemini-2.0-flash-exp', 'gemini-1.5-pro', 'gemini-1.5-flash']
                last_exception = None
                
                for model_name in models_to_try:
                    try:
                        print(f"Trying model: {model_name}...")
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(final_prompt)
                        content = response.text
                        
                        # Robust JSON Extraction
                        start_idx = content.find('[')
                        end_idx = content.rfind(']')
                        
                        if start_idx != -1 and end_idx != -1:
                            json_str = content[start_idx:end_idx+1]
                            return json.loads(json_str), None # Success!
                        else:
                            raise ValueError("No JSON array found")
                            
                    except Exception as e:
                        print(f"Model {model_name} failed: {e}")
                        last_exception = e
                        continue # Try next model
                
                # If we get here, all models failed
                if last_exception:
                    raise last_exception
                    
        except Exception as e:
            error_msg = f"AI generation failed: {str(e)}"
            print(f"{error_msg}. Falling back to heuristic.")
    
    # Smarter Heuristic Fallback for Success Story
    # 1. Clean text
    clean_text = re.sub(r'\[.*?\]', '', text) # Remove timestamps/notes [00:12]
    clean_text = re.sub(r'>>', '', clean_text) # Remove speaker markers >>
    clean_text = re.sub(r'\s+', ' ', clean_text).strip() # Remove extra whitespace/newlines
    
    sentences = re.split(r'(?<=[.!?]) +', clean_text)
    sentences = [s.strip() for s in sentences if len(s) > 30] # Filter short junk
    
    # 2. Extract sections based on keywords (simple heuristic)
    challenges = [s for s in sentences if any(k in s.lower() for k in ["problem", "difficult", "issue", "challenge", "struggle", "lack", "manual"])]
    solutions = [s for s in sentences if any(k in s.lower() for k in ["solution", "implement", "use", "using", "automate", "integrated", "odoo"])]
    results = [s for s in sentences if any(k in s.lower() for k in ["result", "growth", "increase", "save", "faster", "percent", "%"])]
    
    # Fill gaps
    if not challenges: challenges = sentences[:2]
    if not solutions: solutions = sentences[2:4] if len(sentences) > 4 else ["Implemented Odoo ERP"]
    if not results: results = sentences[-3:-1] if len(sentences) > 3 else ["Improved efficiency"]

    # Dynamic Titles (Try to find a short summary sentence or use generic)
    # This is hard without LLM, but we can try to vary it slightly or just keep it safe.
    # We will stick to safe titles but ensure the BODY is rich.

    fallback_content = [
        {
            "subtitle": "Success Story",
            "title": "Transformation Journey", # Changed from generic "How We..."
            "body": "Powered by Metamorphosis - Bangladesh's Leading Odoo Partner"
        },
        {
            "subtitle": "The Challenge",
            "title": "Key Obstacles", # Changed
            "body": challenges[:3] if challenges else ["Manual processes", "Lack of data visibility"]
        },
        {
            "subtitle": "The Solution",
            "title": "Strategic Implementation", # Changed
            "body": solutions[:3] if solutions else ["Automated Manufacturing", "Real-time Dashboards"]
        },
        {
            "subtitle": "The Result",
            "title": "Business Impact", # Changed
            "body": "",
            "stats": [{"value": "100%", "label": "Transformation"}, {"value": "Growth", "label": "Achieved"}] 
        },
        {
            "subtitle": "Partner with Experts",
            "title": "Start Your Journey",
            "body": "Contact Metamorphosis\nLink in bio"
        }
    ]
    
    return fallback_content, error_msg
