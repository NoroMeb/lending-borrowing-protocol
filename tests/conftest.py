import pytest
from web3 import Web3
from scripts.utils import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from brownie import (
    Pool,
    PoolConfigurationMock,
    MockDai,
    network,
    LinkTokenMock,
    MockV3Aggregator,
    PoolLogicMock,
    PriceOracle,
    ReservesManager,
)

PRICE = 10
SUPPLY_AMOUNT = Web3.toWei(100, "ether")
BORROW_AMOUNT = Web3.toWei(75, "ether")


@pytest.fixture()
def skip_live_testing():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing !")


@pytest.fixture()
def account():
    account = get_account()

    return account


@pytest.fixture()
def pool(account):

    pool = Pool.deploy({"from": account})

    return pool


@pytest.fixture()
def pool_configuration(account, pool):
    pool_configuration = PoolConfigurationMock.deploy(pool, {"from": account})

    return pool_configuration


@pytest.fixture()
def pool_logic(account, pool_configuration):
    pool_logic = PoolLogicMock.deploy(pool_configuration, {"from": account})

    return pool_logic


@pytest.fixture()
def dai(account):
    dai = MockDai.deploy({"from": account})

    return dai


@pytest.fixture()
def account_initial_dai_balance(dai, account):

    return dai.balanceOf(account)


@pytest.fixture()
def link(account):
    link = LinkTokenMock.deploy({"from": account})

    return link


@pytest.fixture()
def mock_v3_aggregator(account):
    decimals = 18
    initial_answer = Web3.toWei(PRICE, "ether")
    mock_v3_aggregator = MockV3Aggregator.deploy(
        decimals, initial_answer, {"from": account}
    )

    return mock_v3_aggregator


@pytest.fixture()
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


@pytest.fixture()
def set_pool_configuration_address(account, pool, pool_configuration):
    pool.setPoolConfigurationAddress(pool_configuration, {"from": account})


@pytest.fixture()
def set_pool_logic_address(account, pool, pool_logic):
    pool.setPoolLogicAddress(pool_logic, {"from": account})


@pytest.fixture()
def supply(add_token, set_pool_configuration_address, pool, account, dai):
    dai.approve(pool, SUPPLY_AMOUNT, {"from": account})
    pool.supply(dai, SUPPLY_AMOUNT, {"from": account})


@pytest.fixture()
def withdraw(supply, pool, account, dai):
    pool.withdraw(dai, SUPPLY_AMOUNT, {"from": account})


@pytest.fixture()
def price_oracle(account, mock_v3_aggregator):
    decimals = 18
    price_oracle = PriceOracle.deploy(mock_v3_aggregator, decimals, {"from": account})

    return price_oracle


@pytest.fixture()
def reserves_manager(account, pool_configuration):
    reserves_manager = ReservesManager.deploy(pool_configuration, {"from": account})

    return reserves_manager


@pytest.fixture()
def borrow(supply, dai, pool, set_pool_logic_address, account):
    pool.borrow(dai, BORROW_AMOUNT, {"from": account})
