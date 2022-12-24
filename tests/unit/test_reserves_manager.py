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


def test_update_utilization_rate(reserves_manager):

    # arrange
    total_deposited = SUPPLY_AMOUNT
    total_borrowed = BORROW_AMOUNT

    expexted_utilization_rate = total_borrowed / total_deposited  # basis points

    # act
    utilization_rate = reserves_manager.updateUtilizationRate.call(
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
    variable_borrow_rate = reserves_manager.updateVariableBorrowRate(
        utilization_rate,
        base_variable_borrow_rate,
        interest_rate_slope,
    )

    # assert
    assert variable_borrow_rate / 10**18 == expected_variable_borrow_rate


def test_update_variable_borrow_index(
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
    variable_borrow_index = reserves_manager.updateVariableBorrowIndex(
        Web3.toWei(latest_variable_borrow_index, "ether"),
        Web3.toWei(variable_borrow_rate, "ether"),
        seconds_since_latest_update,  # Web3.toWei(15, "ether")
    )

    # assert
    assert variable_borrow_index / (10**18) == expected_variable_borrow_index


def test_init_reserve(add_token, init_reserve, reserves_manager, dai, account):

    # arrange
    total_deposited = 0
    total_borrowed = 0
    initial_utilization_rate = 0
    initial_variable_borrow_rate = 0
    base_variable_borrow_rate = BASE_VARIABLE_BORROW_RATE
    interest_rate_slope = INTEREST_RATE_SLOPE
    initial_variable_borrow_index = Web3.toWei(1, "ether")
    last_update_time = chain[-1].timestamp
    x_token = add_token[0]
    debt_token = add_token[1]

    # assert
    assert reserves_manager.underlyingAssetToReserve(dai) == (
        total_deposited,
        total_borrowed,
        initial_utilization_rate,
        initial_variable_borrow_rate,
        base_variable_borrow_rate,
        interest_rate_slope,
        initial_variable_borrow_index,
        last_update_time,
        x_token,
        debt_token,
    )


def test_get_reserve(reserves_manager, init_reserve, add_token, dai):

    # arrange
    total_deposited = 0
    total_borrowed = 0
    initial_utilization_rate = 0
    initial_variable_borrow_rate = 0
    base_variable_borrow_rate = BASE_VARIABLE_BORROW_RATE
    interest_rate_slope = INTEREST_RATE_SLOPE
    initial_variable_borrow_index = Web3.toWei(1, "ether")
    last_update_time = chain[-1].timestamp
    x_token = add_token[0]
    debt_token = add_token[1]
    expected_reserve = (
        total_deposited,
        total_borrowed,
        initial_utilization_rate,
        initial_variable_borrow_rate,
        base_variable_borrow_rate,
        interest_rate_slope,
        initial_variable_borrow_index,
        last_update_time,
        x_token,
        debt_token,
    )

    # act / assert
    assert reserves_manager.getReserve(dai) == expected_reserve


def test_update_state(reserves_manager, pool, dai):

    # arrange
    amount = SUPPLY_AMOUNT
    operation = 0  # supply

    # act
    reserves_manager.updateState(dai, amount, operation, {"from": pool})

    # assert
    assert reserves_manager.getReserve(dai)[0] == amount
