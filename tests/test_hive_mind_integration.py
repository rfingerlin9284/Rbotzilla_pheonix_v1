import sys, os
sys.path.insert(0, os.path.abspath('.'))
from PhoenixV2.brain.hive_mind import HiveMindBridge


def test_hive_mind_fetch():
    hb = HiveMindBridge()
    sig = hb.fetch_inference()
    # Accept None or dict, but must not crash
    assert sig is None or isinstance(sig, dict)


if __name__ == '__main__':
    test_hive_mind_fetch()
    print('OK')
