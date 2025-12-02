import os
import json
import re
import google.generativeai as genai

def process_content(text, api_key=None, provider="gemini"):
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
                
                prompt = f"""
                You are a Viral LinkedIn Content Creator. Transform the following video transcript into a high-performing 5-slide carousel.
                
                Transcript:
                {text[:15000]}
                
                **Style Guide:**
                - **Punchy & Direct:** Use short sentences. No fluff.
                - **Hook-Driven:** Slide 1 must stop the scroll.
                - **Value-First:** Slides 2-4 must give actionable advice or shocking stats.
                - **Clear CTA:** Slide 5 must tell them exactly what to do next.
                - **No Corporate Jargon:** Speak like a human.
                
                **Slide Structure:**
                1. **The Hook**: A contrarian statement or a "How to" title. Subtitle: The problem/context.
                2. **The Insight**: The core concept or "Aha!" moment.
                3. **The Method/Story**: How it works or what happened.
                4. **The Result/Why it Matters**: Concrete benefit or takeaway.
                5. **The CTA**: "Follow for more" or "Link in bio".
                
                **Output JSON format ONLY:**
                [
                    {{"title": "STOP DOING THIS", "subtitle": "Common Mistake", "body": "Here is why it kills your growth."}},
                    {{"title": "The Better Way", "subtitle": "Strategy #1", "body": ["Step 1: Do X", "Step 2: Do Y"]}},
                    ...
                ]
                """
                
                response = model.generate_content(prompt)
                content = response.text
                content = re.sub(r'```json\n|\n```', '', content)
                # Clean up any potential markdown formatting in the JSON string
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
