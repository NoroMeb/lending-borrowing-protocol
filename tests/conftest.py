import pytest
from web3 import Web3
from scripts.utils import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from brownie import Pool, MockDai, network, LinkTokenMock


@pytest.fixture
def pool():
    account = get_account()
    pool = Pool.deploy({"from": account})
    return pool


@pytest.fixture
def dai():
    account = get_account()
    dai = MockDai.deploy({"from": account})
    return dai


@pytest.fixture
def link():
    account = get_account()
    link = LinkTokenMock.deploy({"from": account})
    return link


@pytest.fixture
def skip_live_testing():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing !")
