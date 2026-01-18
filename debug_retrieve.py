#!/usr/bin/env python3

import sys

sys.path.append("/home/bhaskar/cd/campusguide")

from retriever.retriever import Retriever


def main():
    retriever = Retriever()

    query = "What documents are students expected to have during placement induction?"

    result = retriever.retrieve(query, role="student")

    print(f"Retrieved {len(result['chunks'])} chunks:")
    print(f"Confidence: {result.get('confidence', 'N/A')}")
    print(f"Query: {result.get('query', 'N/A')}")
    print(f"Role: {result.get('role', 'N/A')}")
    for i, chunk in enumerate(result["chunks"], 1):
        print(f"\nChunk {i}:")
        print(f"Text: {chunk['text'][:200]}...")
        print(f"Metadata: {chunk.get('metadata', {})}")


if __name__ == "__main__":
    main()
