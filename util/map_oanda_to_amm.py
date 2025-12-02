#!/usr/bin/env python3
"""
Map OANDA order IDs (OCO_PLACED/TRADE_OPENED) to AMM trade IDs by matching symbol, side, timestamp proximity, and entry price proximity.
Usage: python3 util/map_oanda_to_amm.py [narration.jsonl]
"""
import sys
import json
import os
from datetime import datetime, timezone



def parse_ts(ts):
    # parse ISO timestamps
    return datetime.fromisoformat(ts.replace('Z', '+00:00'))

            


def pip_size(symbol: str):
    # Standard forex pip for non-JPY is 0.0001, for JPY is 0.01
    if not symbol:
        return 0.0001
    return 0.01 if 'JPY' in symbol else 0.0001


def normalize_price(price):
    try:
        return float(price)
    except Exception:
        return None


def load_events(path):
    oanda_orders = []
    amm_trades = []
    mappings = []
    with open(path, 'r') as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                ev = json.loads(ln)
            except Exception:
                continue
            etype = ev.get('event_type')
            ts = parse_ts(ev['timestamp']) if 'timestamp' in ev else None
            if etype == 'OCO_PLACED' or (etype == 'TRADE_OPENED' and ev.get('venue','').lower().startswith('oanda')) or etype == 'BROKER_ORDER_CREATED':
                details = ev.get('details') or {}
                order_id = details.get('order_id') or details.get('oanda_order') or details.get('order_id')
                # entry price may be 'entry_price' field
                entry = details.get('entry_price') or details.get('entry') or details.get('entry_price')
                side = details.get('direction') or details.get('side')
                oanda_orders.append({
                    'order_id': order_id,
                    'timestamp': ts,
                    'symbol': ev.get('symbol'),
                    'entry': float(entry) if entry is not None else None,
                    'side': side,
                    'etype': etype,
                    'raw': ev,
                })
            if etype == 'BROKER_MAPPING':
                md = ev.get('details') or {}
                mappings.append({'order_id': md.get('order_id'), 'trade_id': md.get('trade_id'), 'timestamp': ts, 'symbol': ev.get('symbol')})
            if etype == 'TRADE_EXECUTED' and ev.get('venue','').lower().startswith('aggressive'):
                details = ev.get('details') or {}
                trade_id = details.get('trade_id')
                entry = details.get('entry')
                side = details.get('side')
                amm_trades.append({
                    'trade_id': trade_id,
                    'timestamp': ts,
                    'symbol': ev.get('symbol'),
                    'entry': float(entry) if entry is not None else None,
                    'side': side,
                    'raw': ev,
                })
    return oanda_orders, amm_trades, mappings


def build_scale_map(oanda_orders, amm_trades):
    """
    Build a per-symbol median scale mapping to normalize AMM prices to OANDA scale.
    If AMM entries appear to be scaled by 100, we detect it and return the median ratio.
    """
    ratios = {}
    # Map amm trades by symbol & approximate timestamp for pairing with oanda orders
    amm_by_symbol = {}
    for t in amm_trades:
        s = (t['symbol'] or '').upper()
        amm_by_symbol.setdefault(s, []).append(t)

    for o in oanda_orders:
        s = (o['symbol'] or '').upper()
        if not o.get('entry') or s not in amm_by_symbol:
            continue
        for t in amm_by_symbol[s]:
            if not t.get('entry'):
                continue
            # Avoid division by zero
            if o.get('entry') is None or o.get('entry') == 0:
                continue
            ratio = None
            try:
                ratio = t['entry'] / float(o['entry'])
            except Exception:
                continue
            if ratio and ratio > 1.5:  # consider only meaningful scaling
                ratios.setdefault(s, []).append(ratio)

    # compute median ratio per symbol
    import math
    scale_map = {}
    for s, rs in ratios.items():
        rs_sorted = sorted(rs)
        if not rs_sorted:
            continue
        mid = len(rs_sorted) // 2
        if len(rs_sorted) % 2 == 1:
            med = rs_sorted[mid]
        else:
            med = (rs_sorted[mid - 1] + rs_sorted[mid]) / 2.0
        # Round to nearest 1 or 10 for stability
        if med > 50:
            med_rounded = round(med / 10) * 10
        elif med > 2:
            med_rounded = round(med)
        else:
            med_rounded = round(med, 2)
        scale_map[s] = med_rounded

    return scale_map


def find_best_match(o, amm_trades, scale_map=None, max_dt=120):
    """
    Find best matching AMM trade for a given OANDA order using an improved scoring heuristic.
    Scoring uses: time difference (seconds) + price difference (in pips * weight)
    Returns (best_trade, score)
    """
    best = None
    best_score = float('inf')
    candidates = []
    for t in amm_trades:
        if (o['symbol'] is None or t['symbol'] is None) or (o['symbol'].replace('_','').lower() != t['symbol'].replace('_','').lower()):
            continue
        # side check
        if o['side'] and t['side'] and o['side'].lower() not in t['side'].lower():
            # not matching side
            continue
        # time diff
        dt = abs((o['timestamp'] - t['timestamp']).total_seconds()) if o['timestamp'] and t['timestamp'] else 1e9
        if dt > max_dt:
            continue
        # price normalize & diff
        o_price = o.get('entry')
        t_price = t.get('entry')
        if o_price is None or t_price is None:
            price_diff = 1e9
        else:
            o_norm = normalize_price(o_price)
            t_norm = normalize_price(t_price)
            if o_norm is None or t_norm is None:
                price_diff = 1e9
            else:
                sym = (o['symbol'] or '').upper()
                # If we have a scale for symbol, use it
                scale = 1.0
                if scale_map and sym in scale_map:
                    scale = float(scale_map[sym])
                else:
                    # Estimate a reasonable scale if AMM price much larger than OANDA price
                    try:
                        if t_norm > 30 and o_norm < 5 and o_norm > 0:
                            est = round(t_norm / o_norm)
                            if est >= 2:
                                scale = float(est)
                    except Exception:
                        scale = 1.0

                # scaled AMM price to OANDA basis
                t_scaled = t_norm / scale if scale != 0 else t_norm
                price_diff = abs(t_scaled - o_norm)
        # convert price difference to pips
        pip = pip_size(o['symbol'])
        price_diff_in_pips = price_diff / pip if pip > 0 else price_diff

        # combine time and price with weighting; favor time slightly
        # score = time_seconds + price_pips * 0.1  (10 pips = 1 sec)
        score = dt + price_diff_in_pips * 0.1
        candidates.append((t, score, dt, price_diff_in_pips))
        if score < best_score:
            best = t
            best_score = score
    # sort candidates by score
    candidates_sorted = sorted(candidates, key=lambda x: x[1])
    return best, best_score, candidates_sorted


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Map OANDA orders to AMM trades')
    parser.add_argument('path', help='Path to narration.jsonl')
    parser.add_argument('--threshold', type=float, default=60.0, help='Acceptance score threshold (lower = stricter)')
    parser.add_argument('--topn', type=int, default=3, help='Top-N candidates to display for each order')
    parser.add_argument('--out', choices=['json', 'csv', 'none'], default='none', help='Optional output format')
    parser.add_argument('--out-file', default='map_oanda_to_amm_output.json', help='Output filename for --out')
    parser.add_argument('--scale-file', default='util/amm_scale_map.json', help='Per-symbol scale cache file')
    parser.add_argument('--recompute-scale', action='store_true', help='Force recomputing scale map even if scale-file exists')
    parser.add_argument('--write', action='store_true', help='Write BROKER_MAPPING events to narration.jsonl for accepted matches (default: dry-run)')
    parser.add_argument('--narration-file', default=None, help='Optional narration file to write BROKER_MAPPING events (overrides env)')
    args = parser.parse_args()
    path = args.path
    # If a narration file override is provided, ensure the writer picks it up
    if args.narration_file:
        os.environ['NARRATION_FILE_OVERRIDE'] = args.narration_file

    # import narration writer after potential override
    from util.narration_logger import log_narration

    oanda_orders, amm_trades, mappings = load_events(path)
    print(f'Loaded {len(oanda_orders)} oanda orders and {len(amm_trades)} AMM trades')
    # Build symbol->scale map to normalize AMM prices into OANDA price space
    scale_map = None
    # Load or compute scale_map
    if args.scale_file and os.path.exists(args.scale_file) and not args.recompute_scale:
        try:
            with open(args.scale_file) as sf:
                scale_map = json.load(sf)
                print(f"Loaded scale_map from {args.scale_file}")
        except Exception:
            scale_map = build_scale_map(oanda_orders, amm_trades)
    else:
        scale_map = build_scale_map(oanda_orders, amm_trades)
        # Save if requested
        try:
            with open(args.scale_file, 'w') as sf:
                json.dump(scale_map, sf, indent=2)
                print(f"Saved scale_map to {args.scale_file}")
        except Exception:
            pass
    if scale_map:
        print('\nDetected AMM price scale mappings by symbol:')
        for s, sc in scale_map.items():
            print(f"  {s}: scale={sc}")
    mapping_dict = {}
    if mappings:
        print('\nExplicit BROKER MAPPING events found in narration:')
        for m in mappings:
            print(f"  {m['order_id']} -> {m['trade_id']} (symbol: {m.get('symbol')}, ts: {m.get('timestamp')})")
            if m.get('order_id') and m.get('trade_id'):
                mapping_dict[m.get('order_id')] = m.get('trade_id')
    # Acceptance threshold controls how confident a heuristic match must be
    acceptance_threshold = args.threshold
    results = []
    for o in oanda_orders:
        # If explicit mapping exists, output and skip heuristic
        oid = o.get('order_id')
        if oid and oid in mapping_dict:
            mapped_tid = mapping_dict[oid]
            # Find the trade object
            trade_obj = next((t for t in amm_trades if t.get('trade_id') == mapped_tid), None)
            if trade_obj:
                out_record = {
                    'order_id': oid,
                    'symbol': o.get('symbol'),
                    'side': o.get('side'),
                    'entry': o.get('entry'),
                    'timestamp': o.get('timestamp').isoformat() if o.get('timestamp') else None,
                    'mapped_trade_id': mapped_tid,
                    'mapped_entry': trade_obj.get('entry'),
                    'mapped_timestamp': trade_obj.get('timestamp').isoformat() if trade_obj.get('timestamp') else None,
                    'explicit_mapping': True,
                    'score': 0.0,
                    'candidates': []
                    , 'confidence': 1.0
                }
                print(f"OANDA order {oid} ({o['symbol']} {o['side']} @ {o['entry']}) at {o['timestamp']} EXPLICITLY MAPPED -> {mapped_tid} @ {trade_obj['entry']} ts={trade_obj['timestamp']}")
                results.append(out_record)
                continue
        match, score, candidates = find_best_match(o, amm_trades, scale_map=scale_map)
        # Accept match only if score <= acceptance_threshold
        topn = args.topn
        if match and score <= acceptance_threshold:
            dt = abs((o['timestamp'] - match['timestamp']).total_seconds()) if o['timestamp'] and match['timestamp'] else None
            print(f"OANDA order {o['order_id']} ({o['symbol']} {o['side']} @ {o['entry']}) at {o['timestamp']} matches AMM {match['trade_id']} @ {match['entry']} at {match['timestamp']} dt={dt}s score={score:.2f}")
            out_record = {
                'order_id': o.get('order_id'),
                'symbol': o.get('symbol'),
                'side': o.get('side'),
                'entry': o.get('entry'),
                'timestamp': o.get('timestamp').isoformat() if o.get('timestamp') else None,
                'mapped_trade_id': match.get('trade_id') if match else None,
                'mapped_entry': match.get('entry') if match else None,
                'mapped_timestamp': match.get('timestamp').isoformat() if match and match.get('timestamp') else None,
                'explicit_mapping': False,
                'score': score,
                'candidates': []
                , 'confidence': max(0.0, min(1.0, 1.0 - (score / (acceptance_threshold if acceptance_threshold > 0 else 1))))
            }
            if args.write:
                try:
                    # Create a mapping event in the narration log
                    log_narration(
                        event_type='BROKER_MAPPING',
                        details={
                            'order_id': o.get('order_id'),
                            'trade_id': match.get('trade_id'),
                            'symbol': o.get('symbol'),
                            'entry_price': o.get('entry'),
                            'mapped_entry': match.get('entry'),
                            'score': score,
                            'confidence': out_record['confidence']
                        },
                        symbol=o.get('symbol'),
                        venue='oanda'
                    )
                    print(f"Wrote BROKER_MAPPING {o.get('order_id')} -> {match.get('trade_id')}")
                except Exception:
                    print(f"Failed to write BROKER_MAPPING for {o.get('order_id')} -> {match.get('trade_id')}")
        else:
            # Either no match found, or score too large
            print(f"OANDA order {o['order_id']} ({o['symbol']} {o['side']} @ {o['entry']}) at {o['timestamp']} NO_MATCH (best_score={score if score is not None else 'N/A'})")
            out_record = {
                'order_id': o.get('order_id'),
                'symbol': o.get('symbol'),
                'side': o.get('side'),
                'entry': o.get('entry'),
                'timestamp': o.get('timestamp').isoformat() if o.get('timestamp') else None,
                'mapped_trade_id': None,
                'mapped_entry': None,
                'mapped_timestamp': None,
                'explicit_mapping': False,
                'score': score if score is not None else None,
                'candidates': [],
                'confidence': 0.0
            }
        # If not exact match, print top candidates for debugging
        if candidates:
            print('  Top candidates:')
            for idx, (t_cand, sc, dt_cand, pips) in enumerate(candidates[:topn]):
                print(f"    {idx+1}. {t_cand['trade_id']} @ {t_cand['entry']} ts={t_cand['timestamp']} dt={dt_cand}s score={sc:.2f} pips={pips:.1f}")
                out_record['candidates'].append({'trade_id': t_cand.get('trade_id'), 'entry': t_cand.get('entry'), 'timestamp': t_cand.get('timestamp').isoformat() if t_cand.get('timestamp') else None, 'score': sc, 'pips': pips})
            results.append(out_record)
    # Write output if requested
    if args.out != 'none':
        if args.out == 'json':
            import json as _json
            with open(args.out_file, 'w') as f:
                _json.dump(results, f, default=str, indent=2)
            print(f"Wrote JSON results to {args.out_file}")
        elif args.out == 'csv':
            import csv as _csv
            keys = ['order_id', 'symbol', 'side', 'entry', 'timestamp', 'mapped_trade_id', 'mapped_entry', 'mapped_timestamp', 'score', 'explicit_mapping']
            with open(args.out_file, 'w', newline='') as f:
                writer = _csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for r in results:
                    row = {k: r.get(k) for k in keys}
                    writer.writerow(row)
            print(f"Wrote CSV results to {args.out_file}")
