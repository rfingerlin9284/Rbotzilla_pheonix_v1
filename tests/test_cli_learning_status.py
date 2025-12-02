import os, sys
import importlib.util
sys.path.insert(0, os.getcwd())
spec = importlib.util.spec_from_file_location("cli", os.path.join(os.getcwd(), 'PhoenixV2', 'interface', 'cli.py'))
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)
show_learning_status = cli.show_learning_status
from PhoenixV2.execution.router import BrokerRouter
from PhoenixV2.core.state_manager import StateManager


class StubAuth:
    def is_live(self):
        return False
    def get_oanda_config(self):
        return {}
    def get_ibkr_config(self):
        return {'host':'127.0.0.1','port':7497,'client_id':1}
    def get_coinbase_config(self):
        return {'key':None,'secret':None}


def test_show_learning_status(tmp_path, capsys):
    auth = StubAuth()
    router = BrokerRouter(auth)
    router.state_manager = StateManager(str(tmp_path / 'state.json'))
    router.state_manager.record_strategy_pnl('liquidity_sweep', 500.0)
    router.state_manager.record_strategy_pnl('liquidity_sweep', -100.0)
    # Call the CLI function
    show_learning_status(router)
    captured = capsys.readouterr()
    assert 'liquidity_sweep' in captured.out
    assert 'Wins' in captured.out or 'PnL' in captured.out
