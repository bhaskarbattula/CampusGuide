#!/usr/bin/env python3

import os
import sys
sys.path.append('/home/bhaskar/cd/campusguide')

from ingestion.document_loader import DocumentLoader

def main():
    loader = DocumentLoader()
    pdf_path = '/home/bhaskar/cd/campusguide/data/raw/ICFAI_Internship_Guidelines-1.pdf'
    
    if not os.path.exists(pdf_path):
        print("PDF not found")
        return
    
    doc = loader.load_document(pdf_path)
    full_text = doc['text']
    print("Full extracted text:")
    print("=" * 50)
    print(full_text)
    print("=" * 50)

if __name__ == "__main__":
    main()