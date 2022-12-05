from scripts.utils import get_account
from unit.test_pool_configuration import test_deploy_pool_configuration, test_add_token
import pytest
from brownie import exceptions, XToken, Contract
from web3 import Web3


def test_set_pool_configuration_address(skip_live_testing, pool, dai):
    # arrange
    skip_live_testing
    account = get_account()
    non_owner = get_account(index=2)
    pool_configuration = test_add_token(skip_live_testing, pool, dai)

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

    # assert
    assert pool.poolConfiguration() == pool_configuration

    return pool, pool_configuration


def test_supply(skip_live_testing, pool, dai, link):
    # arrange
    skip_live_testing
    account = get_account()
    pool, pool_configuration = test_set_pool_configuration_address(
        skip_live_testing, pool, dai
    )
    amount = Web3.toWei(100, "ether")
    dai.approve(pool, amount, {"from": account})
    x_token_address = pool_configuration.getXToken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)

    # assert
    with pytest.raises(exceptions.VirtualMachineError):
        pool.supply(link, amount, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        pool.supply(dai, 0, {"from": account})

    # act
    supply_tx = pool.supply(dai, amount, {"from": account})
    supply_tx.wait(1)
    # assert
    assert dai.balanceOf(x_token_address) == amount
    assert x_token_contract.balanceOf(account) == amount

    return pool, pool_configuration, x_token_contract


def test_withdraw(skip_live_testing, pool, dai, link):
    # arrange
    skip_live_testing
    account = get_account()
    pool, pool_configuration, x_token_contract = test_supply(
        skip_live_testing, pool, dai, link
    )
    amount = Web3.toWei(100, "ether")
    x_token_address = pool_configuration.getXToken(dai)
    initial_dai_account_balance = dai.balanceOf(account)

    # act
    withdraw_tx = pool.withdraw(dai, amount)
    withdraw_tx.wait(1)

    # assert
    assert x_token_contract.balanceOf(account) == 0
    assert dai.balanceOf(x_token_address) == 0
    assert dai.balanceOf(account) == initial_dai_account_balance + amount
