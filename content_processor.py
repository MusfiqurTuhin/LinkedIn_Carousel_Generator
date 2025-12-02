import os
import json
import re
import google.generativeai as genai

def process_content(text, api_key=None, provider="gemini", content_type="Video Takeaway (Summary)"):
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
                
                **Goal:** Create a "{content_type}" carousel.
                """
                
                type_instructions = ""
                if "Success Story" in content_type:
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
                elif "Tutorial" in content_type:
                    # ... (Keep existing or refine)
                    type_instructions = """
                    **Structure (Tutorial):**
                    1. **Hook:** "How to [Achieve Outcome] in 3 Steps".
                    2. **Step 1:** Actionable instruction.
                    3. **Step 2:** Actionable instruction.
                    4. **Step 3:** Actionable instruction.
                    5. **CTA:** "Save this for later."
                    """
                # ... (Keep others)

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
    
    # Smarter Heuristic Fallback
    # 1. Clean text
    clean_text = re.sub(r'\[.*?\]', '', text) # Remove timestamps/notes
    sentences = re.split(r'(?<=[.!?]) +', clean_text)
    sentences = [s.strip() for s in sentences if len(s) > 20] # Filter short junk
    
    # 2. Identify "Key" sentences using keywords
    keywords = ["important", "key", "secret", "result", "success", "fail", "mistake", "strategy", "first", "finally"]
    key_sentences = []
    for s in sentences:
        if any(k in s.lower() for k in keywords):
            key_sentences.append(s)
    
    # Fill with normal sentences if not enough key ones
    if len(key_sentences) < 5:
        key_sentences.extend(sentences[:5])
    
    # Deduplicate and limit
    final_sentences = list(dict.fromkeys(key_sentences))[:4]
    
    return [
        {
            "subtitle": "Key Takeaways",
            "title": "Video Insights",
            "body": "Swipe to see the highlights from this video."
        },
        {
            "subtitle": "Insight #1",
            "title": "Core Concept",
            "body": final_sentences[0] if len(final_sentences) > 0 else "Content loading..."
        },
        {
            "subtitle": "Insight #2",
            "title": "Deep Dive",
            "body": final_sentences[1] if len(final_sentences) > 1 else "Watch video for more."
        },
        {
            "subtitle": "Insight #3",
            "title": "The Impact",
            "body": final_sentences[2] if len(final_sentences) > 2 else "Check the full transcript."
        },
        {
            "subtitle": "Summary",
            "title": "Final Thoughts",
            "body": final_sentences[3] if len(final_sentences) > 3 else "Thanks for watching!"
        }
    ]
