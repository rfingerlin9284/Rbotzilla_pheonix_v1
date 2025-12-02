
import logging
from PhoenixV2.core.mode import is_live

logger = logging.getLogger("Safety")

def safe_place_order(broker_instance, order_packet, method='place_order'):
    symbol = order_packet.get('symbol', order_packet.get('product_id', 'UNKNOWN'))
    _is_live = is_live()
    if _is_live:
        logger.warning(f"⚠️ ATTEMPTING LIVE ORDER ON {symbol}")
    else:
        logger.info(f"📝 PAPER ORDER ON {symbol}")
    try:
        # If broker connector offers a specific API wrapper for placing a safe order, call it
        if method == 'place_order' and hasattr(broker_instance, 'place_order'):
            try:
                resp = broker_instance.place_order(order_packet)
                if isinstance(resp, tuple) and len(resp) == 2:
                    return resp
                if isinstance(resp, dict):
                    return True, resp
            except Exception:
                pass
        try:
            method_func = getattr(broker_instance, method)
        except AttributeError:
            # Fallback to generic place_order if method named not implemented
            method_func = getattr(broker_instance, 'place_order')
        resp = method_func(order_packet)
        # Normalize method override responses to canonical dict if needed
        if isinstance(resp, tuple) and len(resp) == 2:
            ok_flag, data = resp
            if isinstance(data, dict):
                # ensure 'success' key
                data.setdefault('success', bool(ok_flag))
                if not data.get('success') and 'error' not in data:
                    data['error'] = 'Unknown error'
                return bool(ok_flag), data
            else:
                return bool(ok_flag), {'success': bool(ok_flag), 'error': None if ok_flag else str(data), 'raw': data}
        if isinstance(resp, dict):
            resp.setdefault('success', True)
            return True, resp
        return True, {'success': True, 'raw': resp}
    except Exception as e:
        logger.exception("Safety wrapper: error placing order: %s", e)
        return False, {'error': str(e)}
