from conftest import PRICE, SUPPLY_AMOUNT
from web3 import Web3
from brownie import reverts, Contract, XToken


def test_pool_logic_constructor(pool_logic, pool_configuration):

    # assert
    assert pool_logic.poolConfiguration() == pool_configuration


def test_get_user_balance_in_usd(pool_logic, supply, account, dai):

    # act /assert
    assert pool_logic._getUserBalanceInUSD.call(account) == SUPPLY_AMOUNT * PRICE


def test_get_amount_in_usd(add_token, pool_logic, dai):

    # arrange
    amount = Web3.toWei(100, "ether")

    # act / assert
    assert pool_logic._getAmountInUSD.call(amount, dai) == amount * PRICE


def test_validate_borrow_null_amount(supply, pool_logic, account, dai):

    # act / assert
    with reverts("Amount must be greater than 0"):
        pool_logic.validateBorrow(account, dai, 0, {"from": account})


def test_validate_borrow_non_available_token(supply, pool_logic, account, link):

    # arrange
    amount = Web3.toWei(100, "ether")

    # act / assert
    with reverts("token not available"):
        pool_logic.validateBorrow(account, link, amount, {"from": account})


def test_validate_borrow_amount_greater_than_max_amount_in_usd(
    account, supply, pool_logic, dai
):

    # arrange
    amount = Web3.toWei(76, "ether")

    # act / assert
    assert (
        pool_logic.validateBorrow.call(account, dai, amount, {"from": account}) == False
    )


def test_validate_borrow_correct_amount(account, supply, pool_logic, dai):

    # arrange
    amount = Web3.toWei(75, "ether")

    # act / assert
    assert (
        pool_logic.validateBorrow.call(account, dai, amount, {"from": account}) == True
    )


def test_validate_withdraw_null_amount(supply, pool_logic, account, dai):

    # act / assert
    with reverts("Amount must be greater than 0"):
        pool_logic.validateWithdraw(account, dai, 0, {"from": account})


def test_validate_withdraw_non_available_token(supply, pool_logic, account, link):

    # arrange
    amount = Web3.toWei(50, "ether")

    # act / assert
    with reverts("token not available"):
        pool_logic.validateWithdraw(account, link, amount, {"from": account})


def test_validate_withdraw_amount_greater_than_user_balance(
    account, supply, pool_logic, dai
):

    # arrange
    amount = Web3.toWei(101, "ether")

    # act / assert
    assert (
        pool_logic.validateWithdraw.call(account, dai, amount, {"from": account})
        == False
    )


def test_validate_withdraw_correct_amount(account, supply, pool_logic, dai):

    # act / assert
    assert (
        pool_logic.validateWithdraw.call(account, dai, SUPPLY_AMOUNT, {"from": account})
        == True
    )
