"""
AI Module: College ID Card OCR Verification
Uses Tesseract to extract text from uploaded ID card images
and validates college name + roll number format.
"""

import re
import os
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
from dotenv import load_dotenv

load_dotenv()

# Add colleges your app supports
ALLOWED_COLLEGES = [
    'RV COLLEGE', 'RVCE',
    'BMS COLLEGE', 'BMSCE', 'BMSIT',
    'PES UNIVERSITY', 'PESIT', 'PESCE',
    'MSRIT', 'M S RAMAIAH',
    'DAYANANDA SAGAR', 'DSU',
    'CHRIST UNIVERSITY',
    'REVA UNIVERSITY',
    'JAIN UNIVERSITY'
]

# Roll number patterns — add your college format here
ROLL_PATTERNS = [
    r'\b1RV\d{2}[A-Z]{2}\d{3}\b',    # RVCE: 1RV22CS042
    r'\b1BM\d{2}[A-Z]{2}\d{3}\b',    # BMSCE
    r'\b1MS\d{2}[A-Z]{2}\d{3}\b',    # MSRIT
    r'\b\d{2}[A-Z]{2}\d{5}\b',       # Generic format
]


def preprocess_image(image_path: str) -> Image.Image:
    """Enhance image quality before OCR for better accuracy."""
    img = Image.open(image_path).convert('L')       # grayscale
    img = img.filter(ImageFilter.SHARPEN)
    img = ImageEnhance.Contrast(img).enhance(2.0)   # boost contrast
    return img


def verify_id_card(image_path: str) -> dict:
    """
    Extract and validate text from college ID card image.
    Returns verification result with extracted details.
    """
    try:
        img  = preprocess_image(image_path)
        text = pytesseract.image_to_string(img, config='--psm 6').upper()

        # Check college name
        college_found = None
        for college in ALLOWED_COLLEGES:
            if college in text:
                college_found = college
                break

        # Extract roll number
        roll_number = None
        for pattern in ROLL_PATTERNS:
            match = re.search(pattern, text)
            if match:
                roll_number = match.group()
                break

        # Try to extract student name (usually near top of ID)
        lines = [l.strip() for l in text.splitlines()
                 if l.strip() and len(l.strip()) > 2]
        extracted_name = lines[0] if lines else None

        passed = college_found is not None and roll_number is not None

        return {
            'passed':          passed,
            'college_found':   college_found,
            'roll_number':     roll_number,
            'extracted_name':  extracted_name,
            'raw_text':        text[:500],   # first 500 chars only
            'message':         'ID verified' if passed else
                               'Could not detect college name or roll number on ID card'
        }

    except Exception as e:
        return {
            'passed':  False,
            'message': f'OCR processing failed: {str(e)}'
        }
