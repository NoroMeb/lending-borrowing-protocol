from scripts.utils import get_account

from brownie import PoolLogic, exceptions
from unit.test_pool_configuration import test_deploy_pool_configuration, test_add_token

from web3 import Web3

import pytest


def test_deploy_pool_logic(skip_live_testing, pool, dai, mock_v3_aggregator):
    # arrange
    skip_live_testing
    account = get_account()
    pool_configuration, x_token_contract = test_add_token(
        skip_live_testing, pool, dai, mock_v3_aggregator
    )

    # act
    pool_logic = PoolLogic.deploy(pool_configuration.address, {"from": account})

    # assert
    assert pool_logic.poolConfiguration() == pool_configuration.address

    return pool_logic, x_token_contract


def test_get_user_balance_in_usd(skip_live_testing, dai, pool, mock_v3_aggregator):
    # arrange
    skip_live_testing
    account = get_account()
    pool_logic, x_token_contract = test_deploy_pool_logic(
        skip_live_testing, pool, dai, mock_v3_aggregator
    )
    amount = Web3.toWei(1000, "ether")
    x_token_contract.mint(account, amount, {"from": pool})
    # act
    user_balance_in_usd = pool_logic.getUserBalanceInUSD.call(account, dai)

    # assert
    assert user_balance_in_usd == amount * 1000

    return pool_logic


def test_get_amount_in_usd(skip_live_testing, pool, dai, mock_v3_aggregator):
    # arrange
    skip_live_testing
    account = get_account()
    pool_logic, x_token_contract = test_deploy_pool_logic(
        skip_live_testing, pool, dai, mock_v3_aggregator
    )
    amount = Web3.toWei(2, "ether")
    amount_in_usd_expected = Web3.toWei(2, "ether") * 1000

    # act
    amount_in_usd = pool_logic.getAmountInUSD.call(amount, dai, {"from": account})

    # assert
    assert amount_in_usd == amount_in_usd_expected


def test_validate_borrow(skip_live_testing, dai, pool, mock_v3_aggregator, link):
    # arrange
    account = get_account()
    skip_live_testing
    pool_logic = test_get_user_balance_in_usd(
        skip_live_testing, dai, pool, mock_v3_aggregator
    )
    amount_1 = Web3.toWei(1000, "ether")
    amount_2 = Web3.toWei(600, "ether")
    amount_3 = Web3.toWei(750, "ether")

    # act / assert

    with pytest.raises(exceptions.VirtualMachineError):
        pool_logic.validateBorrow.call(account, dai, 0, {"from": account})

    with pytest.raises(exceptions.VirtualMachineError):
        pool_logic.validateBorrow.call(account, link, amount_1, {"from": account})

    assert (
        pool_logic.validateBorrow.call(account, dai, amount_1, {"from": account})
        == False
    )

    assert (
        pool_logic.validateBorrow.call(account, dai, amount_2, {"from": account})
        == True
    )

    assert (
        pool_logic.validateBorrow.call(account, dai, amount_3, {"from": account})
        == True
    )
