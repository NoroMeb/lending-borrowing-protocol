from scripts.utils import get_account
from brownie import reverts, Contract, XToken
from web3 import Web3
from conftest import SUPPLY_AMOUNT


def test_set_pool_configuration_address(
    set_pool_configuration_address, pool, pool_configuration
):

    # assert
    assert pool.poolConfiguration() == pool_configuration


def test_only_owner_can_set_pool_configuration_address(pool, pool_configuration):

    # arrange
    non_owner = get_account(index=2)

    # act / assert
    with reverts():
        pool.setPoolConfigurationAddress(pool_configuration, {"from": non_owner})


def test_supply_null_amount(
    set_pool_configuration_address, add_token, account, pool, dai
):

    # act / assert
    with reverts("insufficient amount"):
        pool.supply(dai, 0, {"from": account})


def test_supply_non_available_token(
    set_pool_configuration_address, add_token, account, pool, link
):

    # arrange
    amount = Web3.toWei(100, "ether")
    link.approve(pool, amount, {"from": account})

    # act / assert
    with reverts("Token not available"):
        pool.supply(link, amount, {"from": account})


def test_supply_transfer_funds_from_supplier_account_to_xtoken(
    account_initial_dai_balance, account, supply, dai, pool_configuration
):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)

    # assert
    assert dai.balanceOf(x_token_address) == SUPPLY_AMOUNT
    assert dai.balanceOf(account) == account_initial_dai_balance - SUPPLY_AMOUNT


def test_supply_mint_xtoken_to_supplier(supply, account, dai, pool_configuration):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)

    # assert
    assert x_token_contract.balanceOf(account) == SUPPLY_AMOUNT


def test_withdraw_null_amount(supply, pool, account, dai):

    # act / assert
    with reverts("Amount must be greater than 0"):
        pool.withdraw(dai, 0, {"from": account})


def test_withdraw_non_available_token(supply, pool, account, link):

    # arrange
    amount = Web3.toWei(100, "ether")
    with reverts("Token not available"):
        pool.withdraw(link, amount, {"from": account})


def test_withdraw_with_no_funds_supplied(
    add_token, set_pool_configuration_address, pool, account, dai
):

    # arrange
    amount = Web3.toWei(100, "ether")
    with reverts("Don't have any funds here"):
        pool.withdraw(dai, amount, {"from": account})


def test_withdraw_transfer_funds_from_xtoken_to_withdrawer(
    withdraw, dai, pool_configuration, account, account_initial_dai_balance
):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)

    # assert
    assert dai.balanceOf(x_token_address) == 0
    assert dai.balanceOf(account) == account_initial_dai_balance


def test_withdraw_burn_withdrawer_xtoken(withdraw, dai, pool_configuration, account):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)

    # assert
    assert x_token_contract.balanceOf(account) == 0
