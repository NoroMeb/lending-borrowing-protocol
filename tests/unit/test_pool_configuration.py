from brownie import Contract, XToken, PriceOracleMock, reverts, DebtToken, chain
from scripts.utils import get_account
from conftest import BASE_VARIABLE_BORROW_RATE, INTEREST_RATE_SLOPE
from web3 import Web3


def test_pool_configuration_constructor(pool_configuration, pool, skip_live_testing):

    # assert
    assert pool_configuration.poolAddress() == pool.address


def test_set_reserve_manager_contract(
    pool_configuration, reserves_manager, account, skip_live_testing
):

    # act
    pool_configuration.setReserveManagerContract(reserves_manager, {"from": account})

    # assert
    assert pool_configuration.reservesManager() == reserves_manager


def test_only_owner_can_set_reserve_manager_contract(
    pool_configuration, reserves_manager, skip_live_testing
):

    # arrange
    non_owner = get_account(index=2)

    # act / assert
    with reverts("Ownable: caller is not the owner"):
        pool_configuration.setReserveManagerContract(
            reserves_manager, {"from": non_owner}
        )


def test_only_owner_can_add_token(
    dai, mock_v3_aggregator, pool_configuration, skip_live_testing
):

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
    pool_configuration, add_token, skip_live_testing
):

    # arrange
    x_token_contract = Contract.from_abi("XToken", add_token[0], XToken.abi)

    # assert
    assert add_token[0] == pool_configuration.getXToken.call()
    assert x_token_contract.name() == "xDAI"


def test_add_token_creates_new_debt_token_instance(
    pool_configuration, add_token, skip_live_testing
):

    # arrange
    debt_token_contract = Contract.from_abi("DebtToken", add_token[1], DebtToken.abi)

    # assert
    assert add_token[1] == pool_configuration.getDebtToken.call()
    assert debt_token_contract.name() == "debtDAI"


def test_add_token_map_underlying_asset_to_x_token(
    add_token, pool_configuration, dai, skip_live_testing
):

    # assert
    assert pool_configuration.underlyingAssetToXtoken(dai) == add_token[0]


def test_add_token_map_underlying_asset_to_debt_token(
    add_token, pool_configuration, dai, skip_live_testing
):

    # assert
    assert pool_configuration.underlyingAssetToDebtToken(dai) == add_token[1]


def test_add_token_map_underlying_asset_to_is_available(
    add_token, pool_configuration, dai, skip_live_testing
):

    # assert
    assert pool_configuration.isAvailable(dai) == True


def test_add_token_creates_new_price_oracle_instance(
    pool_configuration, add_token, mock_v3_aggregator, skip_live_testing
):

    # arrange
    price_oracle_contract = Contract.from_abi(
        "PriceOracleMock", add_token[2], PriceOracleMock.abi
    )

    # assert
    assert add_token[2] == pool_configuration.getPriceOracle.call()
    assert price_oracle_contract.priceFeed() == mock_v3_aggregator


def test_add_token_map_underlying_asset_price_oracle(
    add_token, pool_configuration, dai, skip_live_testing
):

    # assert
    assert pool_configuration.underlyingAssetToPriceOracle(dai) == add_token[2]


def test_add_token_init_new_reserve(
    add_token,
    pool_configuration,
    reserves_manager,
    dai,
    initial_reserve,
    skip_live_testing,
):

    # assert
    assert reserves_manager.getReserve(dai) == initial_reserve


def test_add_token_pushes_underlying_assset_tokens_array(
    add_token, pool_configuration, dai, skip_live_testing
):

    # assert
    assert pool_configuration.tokens(0) == dai
    with reverts():
        pool_configuration.tokens(1)
