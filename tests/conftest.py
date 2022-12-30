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
    ReservesManagerMock,
    chain,
)

PRICE = 10
SUPPLY_AMOUNT = Web3.toWei(100, "ether")
BORROW_AMOUNT = Web3.toWei(75, "ether")
WITHDRAW_AMOUNT = SUPPLY_AMOUNT
INTEREST_RATE_SLOPE = Web3.toWei(5, "ether")
BASE_VARIABLE_BORROW_RATE = Web3.toWei(0, "ether")


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
def pool_configuration_set_reserves_manager_contract(
    pool_configuration, reserves_manager, account
):
    pool_configuration.setReserveManagerContract(reserves_manager, {"from": account})


@pytest.fixture()
def pool_logic(account, pool_configuration):
    pool_logic = PoolLogicMock.deploy(pool_configuration, {"from": account})

    return pool_logic


@pytest.fixture()
def reserves_manager(account, pool_configuration, pool):
    reserves_manager = ReservesManagerMock.deploy(
        pool_configuration,
        pool,
        {"from": account},
    )

    return reserves_manager


@pytest.fixture()
def dai(account):
    dai = MockDai.deploy({"from": account})

    return dai


@pytest.fixture()
def account_initial_dai_balance(dai, account):

    return dai.balanceOf(account)


@pytest.fixture()
def link():
    account = get_account(index=2)
    link = LinkTokenMock.deploy({"from": account})
    link.LinkToken({"from": account})
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
def add_token(
    account,
    dai,
    mock_v3_aggregator,
    pool_configuration,
    pool_configuration_set_reserves_manager_contract,
):
    name = "DAI"
    symbol = "DAI"
    underlying_asset = dai
    price_feed_address = mock_v3_aggregator
    decimals = 18
    base_variable_borrow_rate = BASE_VARIABLE_BORROW_RATE
    interest_rate_slope = INTEREST_RATE_SLOPE

    add_token_tx = pool_configuration.addToken(
        name,
        symbol,
        underlying_asset,
        price_feed_address,
        decimals,
        base_variable_borrow_rate,
        interest_rate_slope,
        {"from": account},
    )

    x_token, debt_token, price_oracle = add_token_tx.return_value

    return x_token, debt_token, price_oracle


@pytest.fixture()
def add_token_link(
    account,
    link,
    mock_v3_aggregator,
    pool_configuration,
    pool_configuration_set_reserves_manager_contract,
):
    name = "LINK"
    symbol = "LINK"
    underlying_asset = link
    price_feed_address = mock_v3_aggregator
    decimals = 18
    base_variable_borrow_rate = BASE_VARIABLE_BORROW_RATE
    interest_rate_slope = INTEREST_RATE_SLOPE

    add_token_tx = pool_configuration.addToken(
        name,
        symbol,
        underlying_asset,
        price_feed_address,
        decimals,
        base_variable_borrow_rate,
        interest_rate_slope,
        {"from": account},
    )

    x_token, debt_token, price_oracle = add_token_tx.return_value

    return x_token, debt_token, price_oracle


@pytest.fixture()
def set_pool_configuration_address(account, pool, pool_configuration):
    pool.setPoolConfigurationAddress(pool_configuration, {"from": account})


@pytest.fixture()
def set_pool_logic_address(account, pool, pool_logic):
    pool.setPoolLogicAddress(pool_logic, {"from": account})


@pytest.fixture()
def set_reserves_manager_address(account, pool, reserves_manager):
    pool.setReservesManagerAddress(reserves_manager, {"from": account})


@pytest.fixture()
def supply(
    add_token,
    set_pool_configuration_address,
    set_reserves_manager_address,
    pool,
    account,
    dai,
):
    dai.approve(pool, SUPPLY_AMOUNT, {"from": account})
    pool.supply(dai, SUPPLY_AMOUNT, {"from": account})


@pytest.fixture()
def price_oracle(account, mock_v3_aggregator):
    decimals = 18
    price_oracle = PriceOracle.deploy(mock_v3_aggregator, decimals, {"from": account})

    return price_oracle


@pytest.fixture()
def borrow(
    supply, dai, pool, set_pool_logic_address, set_reserves_manager_address, account
):
    pool.borrow(dai, BORROW_AMOUNT, dai, {"from": account})


@pytest.fixture()
def withdraw(
    supply, dai, pool, set_pool_logic_address, set_reserves_manager_address, account
):
    pool.withdraw(dai, WITHDRAW_AMOUNT, {"from": account})


@pytest.fixture()
def repay(
    supply,
    borrow,
    pool,
    set_pool_logic_address,
    set_reserves_manager_address,
    dai,
    account,
):
    dai.approve(pool, BORROW_AMOUNT, {"from": account})
    pool.repay(dai, BORROW_AMOUNT, {"from": account})


@pytest.fixture()
def init_reserve(add_token, reserves_manager, dai, pool_configuration):

    x_token = add_token[0]
    debt_token = add_token[1]

    reserves_manager.initReserve(
        dai,
        BASE_VARIABLE_BORROW_RATE,
        INTEREST_RATE_SLOPE,
        x_token,
        debt_token,
        {"from": pool_configuration},
    )


@pytest.fixture()
def initial_reserve(add_token):
    total_deposited = 0
    total_borrowed = 0
    initial_utilization_rate = 0
    initial_variable_borrow_rate = 0
    base_variable_borrow_rate = BASE_VARIABLE_BORROW_RATE
    interest_rate_slope = INTEREST_RATE_SLOPE
    initial_variable_borrow_index = Web3.toWei(1, "ether")
    initial_liquidity_rate = 0
    initial_supply_index = Web3.toWei(1, "ether")
    last_update_time = chain[-1].timestamp
    x_token = add_token[0]
    debt_token = add_token[1]

    return (
        total_deposited,
        total_borrowed,
        initial_utilization_rate,
        initial_variable_borrow_rate,
        base_variable_borrow_rate,
        interest_rate_slope,
        initial_variable_borrow_index,
        initial_liquidity_rate,
        initial_supply_index,
        last_update_time,
        x_token,
        debt_token,
    )


@pytest.fixture()
def reserve(reserves_manager, init_reserve, add_token, dai):
    return reserves_manager.getReserve(dai)
