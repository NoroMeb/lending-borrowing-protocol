from brownie import Contract, XToken, PriceOracle, reverts, DebtToken, chain
from scripts.utils import get_account
from conftest import BASE_VARIABLE_BORROW_RATE, INTEREST_RATE_SLOPE
from web3 import Web3


def test_pool_configuration_constructor(pool_configuration, pool):

    # assert
    assert pool_configuration.poolAddress() == pool.address


def test_only_owner_can_add_token(dai, mock_v3_aggregator, pool_configuration):

    # arrange
    non_owner = get_account(index=2)
    name = "DAI"
    symbol = "DAI"
    underlying_asset = dai
    price_feed_address = mock_v3_aggregator
    decimals = 18
    base_variable_borrow_rate = BASE_VARIABLE_BORROW_RATE
    interest_rate_slope = INTEREST_RATE_SLOPE

    # act / assert
    with reverts():
        add_token_tx = pool_configuration.addToken(
            name,
            symbol,
            underlying_asset,
            price_feed_address,
            decimals,
            base_variable_borrow_rate,
            interest_rate_slope,
            {"from": non_owner},
        )


def test_add_token_creates_new_xtoken_instance(
    pool_configuration,
    add_token,
):

    # arrange
    x_token_contract = Contract.from_abi("XToken", add_token[0], XToken.abi)

    # assert
    assert add_token[0] == pool_configuration.getXToken.call()
    assert x_token_contract.name() == "xDAI"


def test_add_token_creates_new_debt_token_instance(
    pool_configuration,
    add_token,
):

    # arrange
    debt_token_contract = Contract.from_abi("DebtToken", add_token[1], DebtToken.abi)

    # assert
    assert add_token[1] == pool_configuration.getDebtToken.call()
    assert debt_token_contract.name() == "debtDAI"


def test_add_token_map_underlying_asset_to_x_token(add_token, pool_configuration, dai):

    # assert
    assert pool_configuration.underlyingAssetToXtoken(dai) == add_token[0]


def test_add_token_map_underlying_asset_to_debt_token(
    add_token, pool_configuration, dai
):

    # assert
    assert pool_configuration.underlyingAssetToDebtToken(dai) == add_token[1]


def test_add_token_map_underlying_asset_to_is_available(
    add_token, pool_configuration, dai
):

    # assert
    assert pool_configuration.isAvailable(dai) == True


def test_add_token_creates_new_price_oracle_instance(
    pool_configuration, add_token, mock_v3_aggregator
):

    # arrange
    price_oracle_contract = Contract.from_abi(
        "PriceOracle", add_token[2], PriceOracle.abi
    )

    # assert
    assert add_token[2] == pool_configuration.getPriceOracle.call()
    assert price_oracle_contract.priceFeed() == mock_v3_aggregator


def test_add_token_map_underlying_asset_price_oracle(
    add_token, pool_configuration, dai
):

    # assert
    assert pool_configuration.underlyingAssetToPriceOracle(dai) == add_token[2]


def test_init_reserve(pool_configuration, dai, account):

    # arrange
    total_deposited = 0
    total_borrowed = 0
    initial_utilization_rate = 0
    initial_variable_borrow_rate = 0
    base_variable_borrow_rate = BASE_VARIABLE_BORROW_RATE
    interest_rate_slope = INTEREST_RATE_SLOPE
    initial_variable_borrow_index = Web3.toWei(1, "ether")
    last_update_time = chain[-1].timestamp + 1

    # act
    pool_configuration._initReserve(
        dai, base_variable_borrow_rate, interest_rate_slope, {"from": account}
    )

    # assert
    assert pool_configuration.getUnderlyingAssetToReserve(dai) == (
        total_deposited,
        total_borrowed,
        initial_utilization_rate,
        initial_variable_borrow_rate,
        base_variable_borrow_rate,
        interest_rate_slope,
        initial_variable_borrow_index,
        last_update_time,
    )
