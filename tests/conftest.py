import pytest
from web3 import Web3
from scripts.utils import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from brownie import (
    Pool,
    PoolConfiguration,
    MockDai,
    network,
    LinkTokenMock,
    MockV3Aggregator,
)


@pytest.fixture(scope="session")
def skip_live_testing():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing !")


@pytest.fixture(scope="session")
def account():
    account = get_account()

    return account


@pytest.fixture(scope="session")
def pool(account):

    pool = Pool.deploy({"from": account})

    return pool


@pytest.fixture(scope="session")
def pool_configuration(account, pool):
    pool_configuration = PoolConfiguration.deploy(pool, {"from": account})

    return pool_configuration


@pytest.fixture(scope="session")
def dai(account):
    dai = MockDai.deploy({"from": account})

    return dai


@pytest.fixture(scope="session")
def link(account):
    link = LinkTokenMock.deploy({"from": account})

    return link


@pytest.fixture(scope="session")
def mock_v3_aggregator(account):
    decimals = 18
    initial_answer = 10
    mock_v3_aggregator = MockV3Aggregator.deploy(
        decimals, initial_answer, {"from": account}
    )

    return mock_v3_aggregator


@pytest.fixture(scope="session")
def add_token(account, dai, mock_v3_aggregator, pool_configuration):
    name = "xDAI"
    symbol = "xDAI"
    underlying_asset = dai
    price_feed_address = mock_v3_aggregator
    decimals = 18

    add_token_tx = pool_configuration.addToken(
        name, symbol, underlying_asset, price_feed_address, decimals, {"from": account}
    )

    x_token, price_oracle = add_token_tx.return_value

    return x_token, price_oracle
