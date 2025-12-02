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
                You are a LinkedIn Marketing Expert. Analyze the following video transcript and create a 5-slide LinkedIn Carousel.
                
                Transcript:
                {text[:10000]} (truncated if too long)
                
                Goal: Create a compelling success story or educational carousel.
                Structure:
                1. Hook: Catchy Title + Subtitle (Problem/Context).
                2. The Challenge: What was the pain point?
                3. The Solution: How was it solved? (Mention Odoo/Metamorphosis if relevant).
                4. The Results: Concrete numbers, stats, or benefits.
                5. CTA: Call to Action.
                
                Output JSON format ONLY:
                [
                    {{"title": "Slide 1 Title", "subtitle": "Slide 1 Subtitle", "body": "Short body text"}},
                    {{"title": "Slide 2 Title", "subtitle": "Slide 2 Subtitle", "body": ["Bullet 1", "Bullet 2"]}},
                    ...
                ]
                Make the content punchy, professional, and suitable for a business audience.
                """
                
                response = model.generate_content(prompt)
                # Extract JSON from response
                content = response.text
                # Clean markdown code blocks if present
                content = re.sub(r'```json\n|\n```', '', content)
                return json.loads(content)
                
        except Exception as e:
            print(f"LLM Error: {e}. Falling back to heuristic.")
    
    # Heuristic Fallback (Improved)
    sentences = re.split(r'(?<=[.!?]) +', text)
    return [
        {
            "subtitle": "Success Story",
            "title": "Transforming Business with Odoo",
            "body": sentences[0][:120] + "..." if sentences else "Watch the video to learn more."
        },
        {
            "subtitle": "The Challenge",
            "title": "Identifying Key Bottlenecks",
            "body": ["Manual processes slowing down growth", "Lack of real-time data visibility", "Inefficient resource allocation"]
        },
        {
            "subtitle": "The Solution",
            "title": "Strategic Digital Transformation",
            "body": ["Implemented comprehensive Odoo ERP", "Automated core workflows", "Centralized data management"]
        },
        {
            "subtitle": "The Impact",
            "title": "Measurable Business Growth",
            "body": ["Increased operational efficiency", "Better decision making with data", "Scalable infrastructure for future"]
        },
        {
            "subtitle": "Partner with Us",
            "title": "Ready to Write Your Success Story?",
            "body": "Contact Metamorphosis for expert Odoo implementation."
        }
    ]
