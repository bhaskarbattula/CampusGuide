#!/usr/bin/env python3

import sys
sys.path.append('/home/bhaskar/cd/campusguide')

from app import CampusGuideApp

def main():
    app = CampusGuideApp()
    app.ingest_documents()
    print("Ingestion completed.")

if __name__ == "__main__":
    main()