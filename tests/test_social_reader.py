import sys
import os
sys.path.append(os.path.abspath('.'))
from foundation.social_reader import get_social_sentiment_summary


def test_social_summary_basic():
    summary = get_social_sentiment_summary(limit=3)
    assert isinstance(summary, dict)
    assert 'avg_compound' in summary
    assert 'post_count' in summary


if __name__ == '__main__':
    print('Running social_reader simple test...')
    test_social_summary_basic()
    print('OK')
