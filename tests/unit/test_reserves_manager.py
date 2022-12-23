from brownie import ReservesManager, reverts, XToken, Contract, DebtToken, chain
from conftest import (
    SUPPLY_AMOUNT,
    BORROW_AMOUNT,
    INTEREST_RATE_SLOPE,
    BASE_VARIABLE_BORROW_RATE,
)
from web3 import Web3
import time
import pytest


def test_reserves_manager_constructor(account, supply, pool_configuration):

    # act
    reserves_manager = ReservesManager.deploy(
        pool_configuration,
        {"from": account},
    )

    # assert
    assert reserves_manager.poolConfiguration() == pool_configuration


def test_get_reserve_balance(reserves_manager, supply, dai):

    # act / assert
    assert reserves_manager.getReserveBalance(dai) == SUPPLY_AMOUNT


def test_get_reserve_balance_of_non_available_token(reserves_manager, supply, link):

    # act / assert
    with reverts("token not available"):
        reserves_manager.getReserveBalance(link)


def test_update_utilization_rate(
    borrow, reserves_manager, dai, account, pool_configuration
):

    # arrange
    expexted_utilization_rate = BORROW_AMOUNT / SUPPLY_AMOUNT  # basis points

    # act
    utilization_rate = reserves_manager.updateUtilizationRate.call(
        dai, {"from": account}
    )
    print(utilization_rate)

    # assert
    assert utilization_rate / 10**18 == expexted_utilization_rate


def test_update_variable_borrow_rate(
    add_token, reserves_manager, dai, account, pool_configuration, pool
):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)

    debt_token_address = pool_configuration.underlyingAssetToDebtToken(dai)
    debt_token_contract = Contract.from_abi(
        "DebtToken", debt_token_address, DebtToken.abi
    )

    total_deposited = Web3.toWei(100, "ether")
    total_borrowed = Web3.toWei(0.1, "ether")

    x_token_contract.setTotalDeposited(total_deposited, {"from": pool})
    debt_token_contract.setTotalBorrowed(total_borrowed, {"from": pool})

    expected_variable_borrow_rate = 0.005

    # act
    variable_borrow_rate = reserves_manager.updateVariableBorrowRate(
        dai, {"from": account}
    )

    # assert
    assert variable_borrow_rate / 10**18 == expected_variable_borrow_rate


def test_update_variable_borrow_index(
    reserves_manager, dai, account, pool_configuration, pool
):

    # arrange
    seconds_since_latest_update = 10
    variable_rate_per_second = 3.75 / 31536000

    expected_variable_borrow_index = 1 * (
        1 + variable_rate_per_second * seconds_since_latest_update
    )

    # act
    variable_borrow_index_tx = reserves_manager.updateVariableBorrowIndex(
        Web3.toWei(variable_rate_per_second, "ether"),
        seconds_since_latest_update,  # Web3.toWei(15, "ether")
    )

    variable_borrow_index_tx.wait(1)
    variable_borrow_index = variable_borrow_index_tx.return_value

    # assert
    assert (
        variable_borrow_index / (10**18)
        == reserves_manager.variableBorrowIndex() / (10**18)
        == expected_variable_borrow_index
    )


def test_update_state(borrow, reserves_manager, dai, account, pool_configuration, pool):

    # act
    chain.sleep(10)
    chain.mine(1)
    update_state_tx = reserves_manager.updateState(dai)
    variable_borrow_index = update_state_tx.return_value

    # assert
    assert variable_borrow_index == reserves_manager.variableBorrowIndex()
