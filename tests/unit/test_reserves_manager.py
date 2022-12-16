from brownie import ReservesManager, reverts, XToken, Contract
from conftest import (
    SUPPLY_AMOUNT,
    BORROW_AMOUNT,
    INTEREST_RATE_SLOPE,
    BASE_VARIABLE_BORROW_RATE,
)
from web3 import Web3


def test_reserves_manager_constructor(account, supply, pool_configuration):

    # act
    reserves_manager = ReservesManager.deploy(
        pool_configuration,
        INTEREST_RATE_SLOPE,
        BASE_VARIABLE_BORROW_RATE,
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


def test_update_utilization_ration(
    borrow, reserves_manager, dai, account, pool_configuration
):

    # arrange
    expexted_utilization_ratio = (BORROW_AMOUNT / SUPPLY_AMOUNT) * 100  # basis points

    # act
    utilization_ration = reserves_manager.updateUtilizationRatio.call(
        dai, {"from": account}
    )

    # assert
    assert utilization_ration / 10**18 == expexted_utilization_ratio


def test_update_variable_borrow_rate(
    add_token, reserves_manager, dai, account, pool_configuration, pool
):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)
    total_deposited = Web3.toWei(100, "ether")
    total_borrowed = Web3.toWei(0.1, "ether")

    x_token_contract.setTotalDeposited(total_deposited, {"from": pool})
    x_token_contract.setTotalBorrowed(total_borrowed, {"from": pool})

    expected_variable_borrow_rate = 0.004

    # act
    variable_borrow_rate = reserves_manager.updateVariableBorrowRate.call(
        dai, {"from": account}
    )

    # assert
    assert variable_borrow_rate / 10**18 == expected_variable_borrow_rate
