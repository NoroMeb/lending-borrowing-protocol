from conftest import PRICE, SUPPLY_AMOUNT, BORROW_AMOUNT, get_account
from web3 import Web3
from brownie import reverts, Contract, XToken, PriceOracle, DebtToken
import pytest


def test_pool_logic_constructor(pool_logic, pool_configuration):

    # assert
    assert pool_logic.poolConfiguration() == pool_configuration


def test_get_user_balance_in_usd(pool_logic, supply, account, dai):

    # act /assert
    assert pool_logic._getUserBalanceInUSD.call(account, dai) == SUPPLY_AMOUNT * PRICE


def test_get_amount_in_usd(add_token, pool_logic, dai):

    # arrange
    amount = Web3.toWei(100, "ether")

    # act / assert
    assert pool_logic._getAmountInUSD.call(amount, dai) == amount * PRICE


def test_validate_borrow_null_amount(supply, pool_logic, account, dai):

    # act / assert
    with reverts("Amount must be greater than 0"):
        pool_logic.validateBorrow(account, dai, 0, dai, {"from": account})


def test_validate_borrow_non_available_token(supply, pool_logic, account, link):

    # arrange
    amount = Web3.toWei(100, "ether")

    # act / assert
    with reverts("token not available"):
        pool_logic.validateBorrow(account, link, amount, link, {"from": account})


def test_validate_borrow_amount_greater_than_max_amount_in_usd(
    account, supply, pool_logic, dai
):

    # arrange
    amount = Web3.toWei(76, "ether")

    # act / assert
    assert pool_logic.validateBorrow.call(
        account, dai, amount, dai, {"from": account}
    ) == (False, 0)


def test_validate_borrow_correct_amount(account, supply, pool_logic, dai):

    # arrange
    amount = Web3.toWei(75, "ether")

    # act / assert
    assert pool_logic.validateBorrow.call(
        account, dai, amount, dai, {"from": account}
    ) == (True, amount)


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


def test_get_user_debt_in_usd(pool_logic, borrow, account, dai):

    # act /assert
    assert int(
        pool_logic._getUserDebtInUSD.call(account, dai) / (10**18)
    ) == BORROW_AMOUNT * PRICE / (10**18)


def test_get_collateral_amount_to_mint(add_token, pool_logic, dai):

    # arrange
    amount = Web3.toWei(100, "ether")

    # act / assert
    assert pool_logic.getCollateralAmountToMint(dai, amount, dai) == Web3.toWei(
        100, "ether"
    )


def test_validate_liquidation_non_undercollateralized(
    add_token_link,
    supply,
    add_token,
    set_pool_configuration_address,
    set_reserves_manager_address,
    set_pool_logic_address,
    pool_logic,
    pool,
    account,
    dai,
    link,
):

    # arrange
    link.approve(pool, SUPPLY_AMOUNT, {"from": get_account(index=2)})
    pool.supply(link, SUPPLY_AMOUNT, {"from": get_account(index=2)})
    pool.borrow(link, BORROW_AMOUNT, dai, {"from": account})

    # act
    assert pool_logic.validateLiquidation(account, link, dai, SUPPLY_AMOUNT) == (
        False,
        0,
    )


def test_validate_liquidation_undercollateralized(
    add_token_link,
    supply,
    add_token,
    set_pool_configuration_address,
    set_reserves_manager_address,
    set_pool_logic_address,
    pool_logic,
    pool,
    account,
    dai,
    link,
    mock_v3_aggregator_link,
):

    # arrange
    link.approve(pool, SUPPLY_AMOUNT, {"from": get_account(index=2)})
    pool.supply(link, SUPPLY_AMOUNT, {"from": get_account(index=2)})
    pool.borrow(link, BORROW_AMOUNT, dai, {"from": account})

    new_price = Web3.toWei(20, "ether")

    mock_v3_aggregator_link.updateAnswer(new_price)

    # act / assert
    isValid, undercollateralized_amount = pool_logic.validateLiquidation(
        account, link, dai, SUPPLY_AMOUNT
    )
    assert isValid, int(undercollateralized_amount / (10**18)) == (True, 50)
