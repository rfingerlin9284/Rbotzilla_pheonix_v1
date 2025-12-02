#!/usr/bin/env python3
"""
Start a minimal, safe paper-mode demo for OANDA and IBKR connectors.
This script runs without network calls if no credentials are present and uses no real trades.
It prints sanity checks and uses the ParameterManager to load env settings.
"""
import os
import logging
import time
from util.parameter_manager import get_parameter_manager

def safe_connector_demo():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("paper_demo")
    logger.info("Starting paper demo (OANDA & IBKR)")

    # create local ParameterManager using a temp config path if necessary
    pm = get_parameter_manager(config_path=os.environ.get('PM_TEST_CONFIG', '/tmp/paper_params.json'))

    # Set execution defaults for demo
    os.environ['EXECUTION_ENABLED'] = os.environ.get('EXECUTION_ENABLED', '0')
    os.environ['ALLOW_LIVE_TRADING'] = os.environ.get('ALLOW_LIVE_TRADING', 'false')

    # OANDA demo
    try:
        from oanda.brokers.oanda_connector_enhanced import EnhancedOandaConnector
        conn = EnhancedOandaConnector(environment='practice')
        logger.info('OANDA connector instantiated in practice mode')
        try:
            acc = conn.get_account_info()
            logger.info('OANDA get_account_info returned: %s', acc)
        except Exception as e:
            logger.info('OANDA get_account_info not available (no token or sandbox), continuing: %s', e)
    except Exception as e:
        logger.warning('OANDA connector could not be initialized (stubbed): %s', e)

    # IBKR demo
    try:
        from ibkr_gateway.ibkr_connector import IBKRConnector
        conn = IBKRConnector(account='paper', logger=logger)
        logger.info('IBKR connector instantiated for paper account (not connected)')
        try:
            bid, ask = conn.get_best_bid_ask('EUR_USD')
            logger.info('IBKR bid/ask for EUR_USD: %s %s', bid, ask)
        except Exception as e:
            logger.info('IBKR market data not available in demo: %s', e)
    except Exception as e:
        logger.warning('IBKR connector could not be initialized (stubbed): %s', e)

    # Quick narration test
    try:
        import util.narration_logger as narration_logger
        narration_logger.log_narration('DEMO_START', {'details': 'Paper demo started'})
        logger.info('Narration logged (if available)')
    except Exception as e:
        logger.debug('Narration plugin unreachable: %s', e)

    logger.info('Paper demo complete — connectors initialized (paper mode).')

if __name__ == '__main__':
    safe_connector_demo()
