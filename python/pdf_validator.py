#!/usr/bin/env python3
"""
PDF Validator - Validate and sanitize PDF files
"""
import sys
import json
import os
from PyPDF2 import PdfReader, PdfWriter
import pdfplumber
from PIL import Image
import io

def sanitize_pdf(file_path, output_path=None):
    """Remove potentially malicious content from PDF"""
    try:
        reader = PdfReader(file_path)
        writer = PdfWriter()
        
        # Copy only the content pages (strips JavaScript, forms, etc.)
        for page in reader.pages:
            # Remove annotations and links
            if '/Annots' in page:
                del page['/Annots']
            if '/AA' in page:  # Additional actions
                del page['/AA']
            
            writer.add_page(page)
        
        # Remove document-level JavaScript and actions
        if writer._root_object.get('/Names'):
            del writer._root_object['/Names']
        if writer._root_object.get('/AA'):
            del writer._root_object['/AA']
        
        # Write sanitized PDF if output path provided
        if output_path:
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
        
        return True
    except Exception as e:
        return False

def validate_pdf(file_path):
    """Validate PDF file for security and quality"""
    result = {
        "success": True,
        "warnings": [],
        "file_size": 0,
        "page_count": 0,
        "is_text_based": False,
        "readability_score": 0,
        "text_extraction_rate": 0
    }
    
    try:
        # Check file size (2MB limit)
        file_size = os.path.getsize(file_path)
        result["file_size"] = file_size
        
        if file_size > 2 * 1024 * 1024:
            result["success"] = False
            result["error"] = "File size exceeds 2MB limit"
            return result
        
        # Sanitize PDF (in-place check, don't write)
        if not sanitize_pdf(file_path):
            result["warnings"].append("PDF may contain unsupported features")
        
        # Open and analyze PDF
        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            result["page_count"] = page_count
            
            if page_count > 5:
                result["warnings"].append("Resume has more than 5 pages (recommended: 1-2 pages)")
            
            # Extract text and check quality
            total_chars = 0
            extracted_chars = 0
            
            for page in pdf.pages:
                # Try to extract text
                text = page.extract_text()
                
                if text:
                    extracted_chars += len(text.strip())
                
                # Estimate total characters (rough heuristic)
                total_chars += 2000  # Average chars per page
            
            # Calculate text extraction rate
            if total_chars > 0:
                extraction_rate = min(100, (extracted_chars / total_chars) * 100)
                result["text_extraction_rate"] = round(extraction_rate, 2)
            
            # Determine if text-based
            if extracted_chars > 100:
                result["is_text_based"] = True
                result["readability_score"] = min(100, (extracted_chars / (page_count * 500)) * 100)
            else:
                result["success"] = False
                result["error"] = "PDF appears to be image-based or contains no extractable text. Please use a text-based PDF."
                return result
            
            # Additional quality checks
            if result["readability_score"] < 50:
                result["warnings"].append("Low text extraction quality. Consider using a simpler PDF format.")
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"PDF validation failed: {str(e)}"
        }

def main():
    if len(sys.argv) < 2:
        result = {
            "success": False,
            "error": "No file path provided"
        }
        print(json.dumps(result))
        sys.exit(1)
    
    file_path = sys.argv[1]
    result = validate_pdf(file_path)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
