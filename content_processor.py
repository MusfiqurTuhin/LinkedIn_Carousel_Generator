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
                    **Structure (Success Story):**
                    1. **Hook:** The impressive result or transformation. (e.g., "How X grew 50%").
                    2. **The Problem:** What was holding them back? (Pain points).
                    3. **The Solution:** The specific strategy/tool used.
                    4. **The Result:** Concrete numbers/stats.
                    5. **CTA:** "Want similar results? Link in bio."
                    """
                elif "Tutorial" in content_type:
                    type_instructions = """
                    **Structure (Tutorial):**
                    1. **Hook:** "How to [Achieve Outcome] in 3 Steps".
                    2. **Step 1:** Actionable instruction.
                    3. **Step 2:** Actionable instruction.
                    4. **Step 3:** Actionable instruction.
                    5. **CTA:** "Save this for later."
                    """
                elif "Educational" in content_type:
                    type_instructions = """
                    **Structure (Educational/Deep Dive):**
                    1. **Hook:** A contrarian truth or "Everything you know about X is wrong".
                    2. **Concept:** Explain the core concept simply.
                    3. **Why it Matters:** The impact or consequence.
                    4. **Example/Case:** Real world application.
                    5. **CTA:** "Follow for more insights."
                    """
                else: # Video Takeaway
                    type_instructions = """
                    **Structure (Video Takeaway):**
                    1. **Hook:** "I watched [Video Topic] so you don't have to."
                    2. **Key Insight 1:** Most valuable point.
                    3. **Key Insight 2:** Surprising fact.
                    4. **Key Insight 3:** Actionable tip.
                    5. **CTA:** "Watch the full video (Link in comments)."
                    """

                final_prompt = f"""
                {base_prompt}
                {type_instructions}
                
                **Style Guide:**
                - Punchy, direct, no fluff.
                - Use emojis where appropriate.
                
                **Output JSON format ONLY:**
                [
                    {{"title": "Slide 1 Title", "subtitle": "Slide 1 Subtitle", "body": "Body text"}},
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
