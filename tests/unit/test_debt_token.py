from brownie import DebtToken, Contract, reverts
from web3 import Web3


def test_debt_token_constructor(account, dai, pool):

    # arrange
    name = "debtTEST"
    symbol = "debtTEST"
    underlying_asset = dai
    pool_address = pool

    # act
    x_token = DebtToken.deploy(
        name, symbol, underlying_asset, pool_address, {"from": account}
    )

    # assert
    assert x_token.name() == name
    assert x_token.symbol() == name
    assert x_token.poolAddress() == pool_address
    assert x_token.underlyingAsset() == underlying_asset
