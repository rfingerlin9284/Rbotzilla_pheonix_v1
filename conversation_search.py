#!/usr/bin/env python3
"""
Conversation Search Tool for RICK System
Searches through a_convo and other conversation files
"""
import os
import re
import json
from datetime import datetime

def search_conversations(query, file_path="/home/ing/RICK/RICK_LIVE_CLEAN/a_convo"):
    """Search for specific terms in conversation logs"""
    matches = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                if query.lower() in line.lower():
                    matches.append({
                        'line_number': i,
                        'content': line.strip(),
                        'context': ''.join(lines[max(0, i-3):i+3])
                    })
    except FileNotFoundError:
        print(f"Conversation file not found: {file_path}")
    return matches

def get_recent_conversations(days=7):
    """Get conversations from last N days"""
    # Implementation for date-based filtering
    pass

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        results = search_conversations(query)
        print(f"Found {len(results)} matches for '{query}':")
        for match in results[:10]:  # Show first 10
            print(f"Line {match['line_number']}: {match['content'][:100]}...")
    else:
        print("Usage: python3 conversation_search.py <search_term>")
