import os
import json
import re
import google.generativeai as genai

def verify_api_key(api_key):
    """
    Verifies if the provided Gemini API key is valid.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Try a minimal generation to test the key
        response = model.generate_content("Test")
        return True, "API Key is valid!"
    except Exception as e:
        return False, str(e)

def process_content(text, api_key=None, provider="gemini", content_type="Success Story"):
    """
    Analyzes the transcript using an LLM to generate structured carousel content.
    """
    if not text:
        return []

    if api_key:
        try:
            if provider == "gemini":
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Define prompts based on type
                base_prompt = f"""
                You are a Viral LinkedIn Content Creator. Transform the following video transcript into a high-performing 5-slide carousel.
                
                Transcript:
                {text[:15000]}
                
                **Goal:** Create a Success Story carousel.
                """
                
                type_instructions = """
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
                - Subtitle: "Partner with the experts who deliver results."
                - Body: "Contact Metamorphosis".
                """

                final_prompt = f"""
                {base_prompt}
                {type_instructions}
                
                **Style Guide:**
                - Punchy, direct, no fluff.
                - Use emojis where appropriate.
                
                **Output JSON format ONLY:**
                [
                    {{
                        "title": "Slide Title", 
                        "subtitle": "Slide Subtitle", 
                        "body": "Body text or List of strings",
                        "stats": [{{"value": "45%", "label": "Growth"}}] // OPTIONAL: Only for Result slide
                    }},
                    ...
                ]
                """
                
                response = model.generate_content(final_prompt)
                content = response.text
                content = re.sub(r'```json\n|\n```', '', content)
                content = content.strip()
                if content.startswith('```'): content = content[3:]
                if content.endswith('```'): content = content[:-3]
                
                return json.loads(content)
                
        except Exception as e:
            print(f"LLM Error: {e}. Falling back to heuristic.")
    
    # Smarter Heuristic Fallback for Success Story
    # 1. Clean text
    clean_text = re.sub(r'\[.*?\]', '', text) # Remove timestamps/notes
    sentences = re.split(r'(?<=[.!?]) +', clean_text)
    sentences = [s.strip() for s in sentences if len(s) > 20] # Filter short junk
    
    # 2. Extract sections based on keywords (simple heuristic)
    challenges = [s for s in sentences if any(k in s.lower() for k in ["problem", "difficult", "issue", "challenge", "struggle", "lack", "manual"])]
    solutions = [s for s in sentences if any(k in s.lower() for k in ["solution", "implement", "use", "using", "automate", "integrated", "odoo"])]
    results = [s for s in sentences if any(k in s.lower() for k in ["result", "growth", "increase", "save", "faster", "percent", "%"])]
    
    # Fill gaps
    if not challenges: challenges = sentences[:2]
    if not solutions: solutions = sentences[2:4] if len(sentences) > 4 else ["Implemented Odoo ERP"]
    if not results: results = sentences[-3:-1] if len(sentences) > 3 else ["Improved efficiency"]

    return [
        {
            "subtitle": "Success Story",
            "title": "How We Transformed Our Business",
            "body": "Powered by Metamorphosis - Bangladesh's Leading Odoo Partner"
        },
        {
            "subtitle": "The Challenge",
            "title": "Critical Bottlenecks",
            "body": challenges[:3] if challenges else ["Manual processes", "Lack of data visibility"]
        },
        {
            "subtitle": "The Solution",
            "title": "Odoo Implementation",
            "body": solutions[:3] if solutions else ["Automated Manufacturing", "Real-time Dashboards"]
        },
        {
            "subtitle": "The Result",
            "title": "Measurable Growth",
            "body": "",
            "stats": [{"value": "100%", "label": "Digital Transformation"}, {"value": "2x", "label": "Faster Operations"}] # Default placeholders for manual edit
        },
        {
            "subtitle": "Partner with Experts",
            "title": "Ready to Transform?",
            "body": "Contact Metamorphosis\nLink in bio"
        }
    ]
