from brownie import XToken, Contract, reverts
from web3 import Web3
from conftest import SUPPLY_AMOUNT


def test_xtoken_constructor(account, dai, pool):

    # arrange
    name = "TEST"
    symbol = "TEST"
    underlying_asset = dai
    pool_address = pool

    # act
    x_token = XToken.deploy(
        name, symbol, underlying_asset, pool_address, {"from": account}
    )

    # assert
    assert x_token.name() == name
    assert x_token.symbol() == symbol
    assert x_token.poolAddress() == pool_address
    assert x_token.underlyingAsset() == underlying_asset


def test_mint_xtoken(add_token, account, pool, pool_configuration, dai):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)
    amount = Web3.toWei(100, "ether")

    # act
    x_token_contract.mint(account, amount, {"from": pool})

    # assert
    assert x_token_contract.balanceOf(account) == amount


def test_only_pool_can_mint_xtoken(add_token, account, pool, pool_configuration, dai):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)
    amount = Web3.toWei(100, "ether")

    # act / assert
    with reverts("caller must be pool"):
        x_token_contract.mint(account, amount, {"from": account})


def test_burn_xtoken(add_token, account, pool, pool_configuration, dai):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)
    amount = Web3.toWei(100, "ether")
    x_token_contract.mint(account, amount, {"from": pool})

    # act
    x_token_contract.burn(account, amount, {"from": pool})

    # assert
    assert x_token_contract.balanceOf(account) == 0


def test_only_pool_can_burn_xtoken(add_token, account, pool, pool_configuration, dai):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)
    amount = Web3.toWei(100, "ether")
    x_token_contract.mint(account, amount, {"from": pool})

    # act / assert
    with reverts("caller must be pool"):
        x_token_contract.burn(account, amount, {"from": account})


def test_transfer_underlying_asset(
    account_initial_dai_balance, supply, pool_configuration, dai, account, pool
):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)
    amount = SUPPLY_AMOUNT

    # act
    x_token_contract.transferUnderlyingAssetTo(account, amount, {"from": pool})

    # assert
    assert dai.balanceOf(x_token_address) == 0
    assert dai.balanceOf(account) == account_initial_dai_balance


def test_only_pool_can_transfer_underlying_asset(
    supply, pool_configuration, dai, account, pool
):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)
    amount = SUPPLY_AMOUNT

    # act
    with reverts("caller must be pool"):
        x_token_contract.transferUnderlyingAssetTo(account, amount, {"from": account})
