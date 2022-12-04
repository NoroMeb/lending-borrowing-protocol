from scripts.utils import get_account
from brownie import XToken, exceptions, Pool
from web3 import Web3
import pytest


def test_deploy_xtoken(skip_live_testing, pool):
    # arrange
    skip_live_testing
    account = get_account()
    pool = pool
    name = "xTestToken"
    symbol = "xTestToken"

    # act
    x_token = XToken.deploy(name, symbol, pool.address, {"from": account})

    # assert
    assert x_token.name() == name
    assert x_token.symbol() == symbol

    return x_token, pool


def test_mint(skip_live_testing, pool):
    # arrange
    skip_live_testing
    account = get_account()
    x_token, pool = test_deploy_xtoken(skip_live_testing, pool)

    amount = Web3.toWei(100, "ether")

    # act
    mint_tx = x_token.mint(account, amount, {"from": pool})
    mint_tx.wait(1)
    # assert

    assert x_token.balanceOf(account) == amount
    with pytest.raises(exceptions.VirtualMachineError):
        x_token.mint(account, amount)
