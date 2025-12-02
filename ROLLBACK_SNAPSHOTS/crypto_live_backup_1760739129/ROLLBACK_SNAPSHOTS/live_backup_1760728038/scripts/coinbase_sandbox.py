#!/usr/bin/env python3
"""
Coinbase Sandbox Starter

Connects to Coinbase sandbox REST and WebSocket (public) endpoints to subscribe
to ticker/orderbook data. Runs in dry-run mode; will not place live orders.
"""
import asyncio
import json
import os
import sys
from typing import Dict

try:
    import aiohttp
except Exception:
    aiohttp = None


def load_env(path: str) -> Dict[str, str]:
    env = {}
    try:
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip()
    except FileNotFoundError:
        print(f'Env file not found: {path}', file=sys.stderr)
    return env


async def stream_public(product_id='BTC-USD'):
    # Use the Coinbase public sandbox websocket feed for sandbox testing
    url = 'wss://ws-feed-public.sandbox.exchange.coinbase.com'
    if aiohttp is None:
        print('aiohttp not installed; cannot open websocket. Install aiohttp.')
        return
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as ws:
            subscribe = {'type': 'subscribe', 'channels': [{'name': 'ticker', 'product_ids': [product_id]}]}
            await ws.send_json(subscribe)
            print('Subscribed to ticker on', product_id)
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    print('MSG:', msg.data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break


def main():
    env_file = os.path.join(os.path.dirname(__file__), '..', 'env_new.env')
    env = load_env(os.path.abspath(env_file))
    if not env:
        print('No env loaded, aborting.')
        sys.exit(1)

    product = env.get('COINBASE_INSTRUMENTS', 'BTC-USD').split(',')[0]
    print('Dry-run: will stream public market data for', product)
    try:
        asyncio.run(stream_public(product))
    except KeyboardInterrupt:
        print('Stopped by user')


if __name__ == '__main__':
    main()
