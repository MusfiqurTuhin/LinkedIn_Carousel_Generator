import os
import sys
import argparse
from carousel_generator import CarouselGenerator
from youtube_extractor import get_transcript_text
from content_processor import process_content

def main():
    parser = argparse.ArgumentParser(description="Generate LinkedIn Carousel from YouTube Video")
    parser.add_argument("--url", help="YouTube Video URL", required=False)
    parser.add_argument("--logo", help="Path to logo file", default="/Users/musfiqurtuhin/Documents/WorkSpace/LinkedIn/637125294162617682.png")
    parser.add_argument("--output", help="Output directory", default="/Users/musfiqurtuhin/Documents/WorkSpace/LinkedIn_Carousel_Generator/output")
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)
    
    slides_content = []
    
    if args.url:
        print(f"Fetching transcript from {args.url}...")
        text = get_transcript_text(args.url)
        if text:
            print("Processing content...")
            slides_content = process_content(text)
        else:
            print("Failed to extract transcript. Using default content.")
    
    if not slides_content:
        print("Using default/demo content.")
        # Default content (Grameen Danone story)
        slides_content = [
            {
                "subtitle": "Success Story",
                "title": "How Grameen Danone Scaled Social Impact with Odoo",
                "body": "Powered by Metamorphosis - Bangladesh's Leading Odoo Partner"
            },
            {
                "subtitle": "The Challenge",
                "title": "Overcoming Operational Bottlenecks",
                "body": [
                    "Manual, disconnected supply chain processes",
                    "Lack of real-time financial data",
                    "Difficulty tracking impact across rural distribution"
                ]
            },
            {
                "subtitle": "The Solution",
                "title": "A Comprehensive Odoo Ecosystem",
                "body": [
                    "Automated Manufacturing & Inventory Management",
                    "Integrated Accounting for financial clarity",
                    "Real-time Dashboards for data-driven decisions"
                ]
            },
            {
                "subtitle": "The Result",
                "title": "Measurable Impact & Growth",
                "body": [
                    "45% Business Growth in 1 Year",
                    "50% Faster Manufacturing Process",
                    "Empowered decision-making with real-time data"
                ]
            },
            {
                "subtitle": "Partner with Experts",
                "title": "Ready to Transform Your Business?",
                "body": "Metamorphosis delivers results. Let's discuss your success story."
            }
        ]

    print("Initializing Generator...")
    generator = CarouselGenerator(logo_path=args.logo)
    
    print(f"Generating {len(slides_content)} slides...")
    for i, slide in enumerate(slides_content):
        path = generator.generate_slide(slide, i + 1, len(slides_content), args.output)
        print(f"Generated: {path}")

    print(f"Done! Images are in {args.output}")

if __name__ == "__main__":
    main()
