from brownie import ReservesManager, reverts
from conftest import SUPPLY_AMOUNT


def test_reserves_manager_constructor(account, supply, pool_configuration):

    # act
    reserves_manager = ReservesManager.deploy(pool_configuration, {"from": account})

    # assert
    assert reserves_manager.poolConfiguration() == pool_configuration


def test_get_reserve_balance(reserves_manager, supply, dai):

    # act / assert
    assert reserves_manager.getReserveBalance(dai) == SUPPLY_AMOUNT


def test_get_reserve_balance_of_non_available_token(reserves_manager, supply, link):

    # act / assert
    with reverts("Token not available"):
        reserves_manager.getReserveBalance(link)
