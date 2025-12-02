"""
Configuration file for LinkedIn Carousel Generator
Contains templates, color schemes, fonts, and default settings
"""

# Content Templates
CONTENT_TYPES = {
    "Success Story": {
        "description": "Client success story with problem-solution-result structure",
        "slides": 5,
        "structure": ["Hook", "Challenge", "Solution", "Result", "CTA"]
    },
    "Tutorial": {
        "description": "Step-by-step guide or how-to content",
        "slides": 5,
        "structure": ["Introduction", "Step 1", "Step 2", "Step 3", "Conclusion"]
    },
    "Tips & Tricks": {
        "description": "Quick actionable advice and insights",
        "slides": 5,
        "structure": ["Hook", "Tips", "Best Practices", "Common Mistakes", "CTA"]
    },
    "Data Insights": {
        "description": "Statistics and data-driven content",
        "slides": 5,
        "structure": ["Introduction", "Key Stat 1", "Key Stat 2", "Analysis", "Takeaway"]
    }
}

# Color Schemes
COLOR_SCHEMES = {
    "Modern Tech": {
        "primary": "#714B67",
        "secondary": "#017E84",
        "description": "Professional purple and teal"
    },
    "Startup Orange": {
        "primary": "#FF6B35",
        "secondary": "#004E89",
        "description": "Energetic orange and navy"
    },
    "Corporate Navy": {
        "primary": "#1E3A8A",
        "secondary": "#10B981",
        "description": "Traditional navy and green"
    },
    "Creative Magenta": {
        "primary": "#D946EF",
        "secondary": "#F59E0B",
        "description": "Bold magenta and amber"
    },
    "Professional Slate": {
        "primary": "#475569",
        "secondary": "#0EA5E9",
        "description": "Neutral slate and sky blue"
    },
    "Elegant Violet": {
        "primary": "#7C3AED",
        "secondary": "#EC4899",
        "description": "Vibrant violet and pink"
    }
}

# Font Options
FONT_OPTIONS = {
    "Inter": {
        "url": "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap",
        "description": "Modern, clean, versatile"
    },
    "Poppins": {
        "url": "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap",
        "description": "Friendly, geometric, rounded"
    },
    "Montserrat": {
        "url": "https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap",
        "description": "Bold, impactful, contemporary"
    },
    "Roboto": {
        "url": "https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap",
        "description": "Clean, modern, professional"
    },
    "Space Grotesk": {
        "url": "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap",
        "description": "Tech-forward, geometric"
    }
}

# Background Modes
BACKGROUND_MODES = {
    "Solid Color": "Clean white or custom color background",
    "Gradient Pattern": "Animated gradient mesh overlay",
    "Uploaded Image": "Custom background image with opacity control",
    "Geometric Pattern": "Modern geometric shapes and patterns"
}

# Default Settings
DEFAULT_SETTINGS = {
    "font": "Inter",
    "color_scheme": "Modern Tech",
    "bg_mode": "Gradient Pattern",
    "bg_opacity": 0.15,
    "author_handle": "@metamorphosis",
    "brand_name": "Metamorphosis",
    "content_type": "Success Story",
    "output_format": "PNG",
    "resolution": "1080x1080"
}

# Export Options
EXPORT_FORMATS = ["PNG", "JPEG", "WebP"]
RESOLUTION_OPTIONS = {
    "LinkedIn Standard": (1080, 1080),
    "High Quality": (2160, 2160),
    "Print Quality": (3240, 3240)
}

# Content Generation Settings
AI_SETTINGS = {
    "max_transcript_length": 15000,
    "fallback_enabled": True,
    "content_tone": ["Professional", "Casual", "Inspirational", "Educational"],
    "models_priority": ['gemini-3-pro-preview', 'gemini-2.5-pro', 'gemini-2.5-flash']
}
