#!/usr/bin/env python3
"""
Simple script to test social_reader functionality.
Prints Reddit configuration (redacted) and a sample sentiment summary.
"""
import os
import sys
sys.path.append(os.path.abspath('.'))
from foundation.env_manager import get_market_data_config, redact
from foundation.social_reader import get_social_sentiment_summary


def main():
    cfg = get_market_data_config()
    print('Market data configuration (redacted):')
    for k, v in cfg.items():
        print(f"- {k}: {redact(v) if v else '<MISSING>'}")

    try:
        summary = get_social_sentiment_summary(limit=5)
        print('\nSocial Sentiment Summary:')
        print(f"Source: {summary.get('source')}")
        print(f"Subreddits: {summary.get('subreddits')}")
        print(f"Post Count: {summary.get('post_count')}")
        print(f"Avg Compound: {summary.get('avg_compound'):.3f}")
        print('\nSample posts:')
        for p in summary.get('raw_posts', []):
            print(f" - {p.get('title')[:120]} | {p.get('url')}")
    except Exception as e:
        print('Failed to get social sentiment:', e)

if __name__ == '__main__':
    main()
