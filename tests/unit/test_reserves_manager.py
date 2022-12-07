from scripts.utils import get_account
from unit.test_pool_configuration import test_add_token
from brownie import ReservesManager, exceptions
import pytest


def test_deploy_reserves_manager(skip_live_testing, pool, dai, mock_v3_aggregator):
    # arrange
    skip_live_testing
    account = get_account()
    pool_configuration, x_token_contract = test_add_token(
        skip_live_testing, pool, dai, mock_v3_aggregator
    )

    # act
    reserves_manager = ReservesManager.deploy(pool_configuration, {"from": account})

    # assert
    assert reserves_manager.poolConfiguration() == pool_configuration

    return reserves_manager


def test_get_reserve_balance(skip_live_testing, pool, dai, link, mock_v3_aggregator):
    # arrange
    skip_live_testing
    reserves_manager = test_deploy_reserves_manager(
        skip_live_testing, pool, dai, mock_v3_aggregator
    )

    # act / assert
    with pytest.raises(exceptions.VirtualMachineError):
        reserves_manager.getReserveBalance(link)
    assert reserves_manager.getReserveBalance(dai) == 0

    pass
