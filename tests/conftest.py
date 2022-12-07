import pytest
from web3 import Web3
from scripts.utils import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from brownie import Pool, MockDai, network, LinkTokenMock, MockV3Aggregator


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


@pytest.fixture()
def mock_v3_aggregator():
    account = get_account()
    decimals = 18
    price = 1000
    price_in_wei = Web3.toWei(price, "ether")
    mock_v3_aggregator = MockV3Aggregator.deploy(
        decimals, price_in_wei, {"from": account}
    )

    return mock_v3_aggregator
