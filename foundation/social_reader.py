"""
foundation.social_reader
------------------------
Small social data integration module. Supports Reddit (PRAW) and falls back to
Reddit OAuth via `requests` if PRAW is not present. Computes VADER-based
sentiment summary for fetched posts.

This module intentionally uses a lightweight approach for sentiment to avoid
heavy ML dependencies. It is meant for lightweight, quick environmental
signals that feed into QuantHedgeRules.
"""
from typing import List, Dict, Any, Optional
import os
import logging
from time import sleep

try:
    import praw
except Exception:
    praw = None
try:
    import requests
except Exception:
    requests = None
try:
    import feedparser
except Exception:
    feedparser = None

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except Exception:
    SentimentIntensityAnalyzer = None

from foundation.env_manager import get_market_data_config, redact

logger = logging.getLogger(__name__)


def _ensure_vader():
    if SentimentIntensityAnalyzer is None:
        return None
    return SentimentIntensityAnalyzer()


def get_reddit_client() -> Optional[Any]:
    cfg = get_market_data_config()
    cid = cfg.get('REDDIT_CLIENT_ID')
    csec = cfg.get('REDDIT_CLIENT_SECRET')
    user_agent = cfg.get('REDDIT_USER_AGENT')
    if not cid or not csec or not user_agent:
        logger.debug('Reddit credentials missing in env; social_reader will skip Reddit')
        return None
    if praw:
        return praw.Reddit(client_id=cid, client_secret=csec, user_agent=user_agent)
    # Fallback to requests-based public endpoints (limited) using simple OAuth2
    return {'cid': cid, 'csec': csec, 'user_agent': user_agent}


def get_reddit_posts(subreddits: str = 'news', limit: int = 10) -> List[Dict[str, Any]]:
    client = get_reddit_client()
    if not client:
        return []
    if isinstance(client, dict):
        # Basic requests-based fallback: fetch top posts via public JSON endpoint (no auth)
        posts = []
        headers = {'User-Agent': client['user_agent']}
        for sub in subreddits.split(','):
            sub = sub.strip()
            url = f'https://www.reddit.com/r/{sub}/hot.json?limit={limit}'
            try:
                if not requests:
                    logger.debug('requests not available; cannot fetch reddit fallback')
                    continue
                r = requests.get(url, headers=headers, timeout=10)
                if r.status_code == 200:
                    meta = r.json().get('data', {}).get('children', [])
                    for item in meta:
                        d = item.get('data', {})
                        posts.append({'title': d.get('title'), 'selftext': d.get('selftext'), 'url': d.get('url')})
                else:
                    logger.debug(f'Reddit fallback request failed for {sub}: {r.status_code}')
            except Exception as e:
                logger.debug(f'Reddit fallback request exception: {e}')
        return posts

    # PRAW client
    posts = []
    for sub in subreddits.split(','):
        sub = sub.strip()
        try:
            subreddit = client.subreddit(sub)
            for p in subreddit.hot(limit=limit):
                posts.append({'title': p.title, 'selftext': getattr(p, 'selftext', ''), 'url': p.url})
            sleep(0.5)
        except Exception as e:
            logger.debug(f'PRAW fetch failed for {sub}: {e}')
    return posts


def get_hackernews_posts(limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch top Hacker News posts via the public Firebase API"""
    try:
        if not requests:
            return []
        ids_url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
        r = requests.get(ids_url, timeout=10)
        if r.status_code != 200:
            return []
        ids = r.json()[:limit]
        posts = []
        for i in ids:
            url = f'https://hacker-news.firebaseio.com/v0/item/{i}.json'
            ri = requests.get(url, timeout=10)
            if ri.status_code == 200:
                d = ri.json()
                posts.append({'title': d.get('title'), 'url': d.get('url', f'https://news.ycombinator.com/item?id={i}'), 'selftext': d.get('text', '')})
        return posts
    except Exception:
        return []


def get_google_news_rss(topic: str = 'finance', limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch Google News RSS for a given topic (search query)"""
    try:
        if not feedparser:
            return []
        from urllib.parse import quote_plus
        query = quote_plus(topic)
        url = f'https://news.google.com/rss/search?q={query}'
        feed = feedparser.parse(url)
        posts = []
        for entry in feed.entries[:limit]:
            posts.append({'title': entry.get('title'), 'url': entry.get('link'), 'selftext': entry.get('summary', '')})
        return posts
    except Exception:
        return []


def analyze_sentiment_text(texts: List[str]) -> Dict[str, Any]:
    if not texts:
        return {'count': 0, 'avg_compound': 0.0, 'details': {}}
    analyzer = _ensure_vader()
    total = 0.0
    details = []
    # If vader is available, use it; otherwise use a simple lexicon-based fallback
    if analyzer:
        for t in texts:
            vs = analyzer.polarity_scores(t)
            details.append(vs)
            total += vs.get('compound', 0.0)
    else:
        # Fallback: simple token counting - naive but effective for quick signal
        POSITIVE = {'gain', 'gains', 'up', 'surge', 'bull', 'positive', 'rally', 'pump', 'win', 'wins'}
        NEGATIVE = {'loss', 'losses', 'down', 'crash', 'bear', 'negative', 'selloff', 'drop', 'dump'}
        for t in texts:
            tokens = set([w.strip('.,!?:;()[]').lower() for w in t.split() if w.strip()])
            pos = len(tokens & POSITIVE)
            neg = len(tokens & NEGATIVE)
            compound = (pos - neg) / (pos + neg) if (pos + neg) > 0 else 0.0
            vs = {'compound': compound, 'pos': pos, 'neg': neg}
            details.append(vs)
            total += compound
    avg = total / len(texts)
    return {'count': len(texts), 'avg_compound': avg, 'details': details}


def get_social_sentiment_summary(subreddits: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
    config = get_market_data_config()
    if not subreddits:
        subreddits = config.get('REDDIT_SUBREDDITS') or 'news,finance,cryptocurrency'
    posts = []
    # Reddit
    try:
        posts += get_reddit_posts(subreddits=subreddits, limit=limit)
    except Exception:
        pass
    # Hacker News (top stories)
    try:
        posts += get_hackernews_posts(limit=limit)
    except Exception:
        pass
    # Google News / RSS (finance search)
    try:
        posts += get_google_news_rss(topic='finance', limit=limit)
    except Exception:
        pass
    titles = [p.get('title', '') + ' ' + (p.get('selftext') or '') for p in posts]
    sentiment = analyze_sentiment_text(titles)
    return {
        'source': 'reddit',
        'subreddits': subreddits,
        'post_count': sentiment['count'],
        'avg_compound': sentiment['avg_compound'],
        'raw_posts': posts[:5],  # store a small sample
    }
