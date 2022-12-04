from scripts.utils import get_account
from unit.test_pool_configuration import test_deploy_pool_configuration
import pytest
from brownie import exceptions


def test_set_pool_configuration_address(skip_live_testing, pool):
    # arrange
    skip_live_testing
    account = get_account()
    non_owner = get_account(index=2)
    pool = pool
    pool_configuration = test_deploy_pool_configuration(skip_live_testing, pool)

    # assert
    with pytest.raises(exceptions.VirtualMachineError):
        pool.setPoolConfigurationAddress(
            pool_configuration.address, {"from": non_owner}
        )

    # act
    set_pool_configuration_address_tx = pool.setPoolConfigurationAddress(
        pool_configuration.address, {"from": account}
    )
    set_pool_configuration_address_tx.wait(1)
