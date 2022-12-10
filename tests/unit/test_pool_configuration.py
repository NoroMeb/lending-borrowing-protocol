from brownie import Contract, XToken, PriceOracle, reverts
from scripts.utils import get_account


def test_pool_configuration_constructor(pool_configuration, pool):

    # assert
    assert pool_configuration.poolAddress() == pool.address


def test_only_owner_can_add_token(dai, mock_v3_aggregator, pool_configuration):

    # arrange
    non_owner = get_account(index=2)
    name = "xDAI"
    symbol = "xDAI"
    underlying_asset = dai
    price_feed_address = mock_v3_aggregator
    decimals = 18

    # act / assert
    with reverts():
        add_token_tx = pool_configuration.addToken(
            name,
            symbol,
            underlying_asset,
            price_feed_address,
            decimals,
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


def test_add_token_map_underlying_asset_to_x_token(add_token, pool_configuration, dai):

    # assert
    assert pool_configuration.underlyingAssetToXtoken(dai) == add_token[0]


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
        "PriceOracle", add_token[1], PriceOracle.abi
    )

    # assert
    assert add_token[1] == pool_configuration.getPriceOracle.call()
    assert price_oracle_contract.priceFeed() == mock_v3_aggregator


def test_add_token_map_underlying_asset_price_oracle(
    add_token, pool_configuration, dai
):

    # assert
    assert pool_configuration.underlyingAssetToPriceOracle(dai) == add_token[1]
