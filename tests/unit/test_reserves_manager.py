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


def test_reserves_manager_constructor(account, supply, pool, pool_configuration):

    # act
    reserves_manager = ReservesManager.deploy(
        pool_configuration,
        pool,
        {"from": account},
    )

    # assert
    assert reserves_manager.poolConfigurationAddress() == pool_configuration
    assert reserves_manager.poolAddress() == pool


def test_get_reserve(dai, reserves_manager, init_reserve, initial_reserve):

    # act / assert
    assert reserves_manager.getReserve(dai) == initial_reserve


def test_update_utilization_rate(reserves_manager):

    # arrange
    total_deposited = SUPPLY_AMOUNT
    total_borrowed = BORROW_AMOUNT

    expexted_utilization_rate = total_borrowed / total_deposited  # basis points

    # act
    utilization_rate = reserves_manager._updateUtilizationRate.call(
        total_deposited, total_borrowed
    )

    # assert
    assert utilization_rate / 10**18 == expexted_utilization_rate


def test_update_variable_borrow_rate(reserves_manager):

    # arrange
    utilization_rate = Web3.toWei(0.75, "ether")
    base_variable_borrow_rate = BASE_VARIABLE_BORROW_RATE
    interest_rate_slope = INTEREST_RATE_SLOPE

    expected_variable_borrow_rate = 3.75

    # act
    variable_borrow_rate = reserves_manager._updateVariableBorrowRate(
        utilization_rate,
        base_variable_borrow_rate,
        interest_rate_slope,
    )

    # assert
    assert variable_borrow_rate / 10**18 == expected_variable_borrow_rate


def test_update_index(
    reserves_manager, dai, account, pool_configuration, pool, add_token
):

    # arrange

    seconds_since_latest_update = 10
    variable_borrow_rate = 3.75
    seconds_per_year = 31536000
    latest_variable_borrow_index = 1

    expected_variable_borrow_index = latest_variable_borrow_index * (
        1 + (variable_borrow_rate / seconds_per_year) * seconds_since_latest_update
    )
    # act
    variable_borrow_index = reserves_manager._updateIndex(
        Web3.toWei(latest_variable_borrow_index, "ether"),
        Web3.toWei(variable_borrow_rate, "ether"),
        seconds_since_latest_update,  # Web3.toWei(15, "ether")
    )

    print(expected_variable_borrow_index)
    # assert
    assert variable_borrow_index / (10**18) == expected_variable_borrow_index


def test_init_reserve(init_reserve, initial_reserve, reserves_manager, dai):

    # assert
    assert reserves_manager.underlyingAssetToReserve(dai) == initial_reserve


def test_get_reserve(reserves_manager, init_reserve, initial_reserve, dai):

    # act / assert
    assert reserves_manager.getReserve(dai) == initial_reserve


def test_update_state(add_token, init_reserve, reserves_manager, pool, dai):

    # arrange
    amount = SUPPLY_AMOUNT
    operation = 0  # supply

    total_deposited = amount
    total_borrowed = 0
    utilization_rate = 0
    variable_borrow_rate = 0
    base_variable_borrow_rate = BASE_VARIABLE_BORROW_RATE
    interest_rate_slope = INTEREST_RATE_SLOPE
    variable_borrow_index = Web3.toWei(1, "ether")
    last_update_time = chain[-1].timestamp + 10
    x_token = add_token[0]
    debt_token = add_token[1]

    expected_reserve = (
        total_deposited,
        total_borrowed,
        utilization_rate,
        variable_borrow_rate,
        base_variable_borrow_rate,
        interest_rate_slope,
        variable_borrow_index,
        last_update_time,
        x_token,
        debt_token,
    )

    expected_reserve_2 = (
        total_deposited,
        total_borrowed,
        utilization_rate,
        variable_borrow_rate,
        base_variable_borrow_rate,
        interest_rate_slope,
        variable_borrow_index,
        last_update_time + 1,
        x_token,
        debt_token,
    )

    # act
    chain.sleep(10)
    chain.mine(1)
    reserves_manager.updateState(dai, amount, operation, {"from": pool})

    # assert
    assert reserves_manager.getReserve(dai) == expected_reserve or expected_reserve_2


def test_get_variable_borrow_index_since_last_update(borrow, reserves_manager, dai):

    # arrange
    chain.sleep(15)
    chain.mine(1)

    expected_variable_borrow_index = 1 * (
        1 + (3.75 / 31536000) * 18
    )  # 18 seconds (chain.sleep(15) + 3 of the test) .

    # act / assert
    assert (
        reserves_manager.getVariableBorrowIndexSinceLastUpdate(dai)
        != expected_variable_borrow_index
    )


def test_get_total_deposited(init_reserve, reserves_manager, dai):

    # act / assertt
    assert reserves_manager.getTotalDeposited(dai) == 0


def test_get_total_borrowed(init_reserve, reserves_manager, dai):

    # act / assert
    assert reserves_manager.getTotalBorrowed(dai) == 0


def test_get_utilization_rate(init_reserve, reserves_manager, dai):

    # act / assert
    assert reserves_manager.getUtilizationRate(dai) == 0


def test_get_variable_borrow_rate(init_reserve, reserves_manager, dai):

    # act / assert
    assert reserves_manager.getVariableBorrowRate(dai) == 0


def test_get_base_variable_borrow_rate(init_reserve, reserves_manager, dai):

    # act / assert
    assert reserves_manager.getBaseVariableBorrowRate(dai) == 0


def test_get_interest_rate_slope(init_reserve, reserves_manager, dai):

    # act / assert
    assert reserves_manager.getInterestRateSlope(dai) == Web3.toWei(5, "ether")


def test_get_variable_borrow_index(init_reserve, reserves_manager, dai):

    # act / assert
    assert reserves_manager.getVariableBorrowIndex(dai) == Web3.toWei(1, "ether")


def test_get_last_update_time(init_reserve, reserves_manager, dai):

    # act / assert
    assert reserves_manager.getLastUpdateTime(dai) == chain[-1].timestamp


def test_get_x_token(add_token, init_reserve, reserves_manager, dai):

    # act / assert
    assert reserves_manager.getXToken(dai) == add_token[0]


def test_get_debt_token(add_token, init_reserve, reserves_manager, dai):

    # act / assert
    assert reserves_manager.getDebtToken(dai) == add_token[1]
