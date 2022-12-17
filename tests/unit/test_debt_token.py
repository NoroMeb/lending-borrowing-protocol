from brownie import DebtToken, Contract, reverts, DebtToken
from web3 import Web3
from scripts.utils import get_account


def test_debt_token_constructor(account, dai, pool):

    # arrange
    name = "debtTEST"
    symbol = "debtTEST"
    underlying_asset = dai
    pool_address = pool

    # act
    x_token = DebtToken.deploy(
        name, symbol, underlying_asset, pool_address, {"from": account}
    )

    # assert
    assert x_token.name() == name
    assert x_token.symbol() == name
    assert x_token.poolAddress() == pool_address
    assert x_token.underlyingAsset() == underlying_asset


def test_mint_debt_token(add_token, account, pool, pool_configuration, dai):

    # arrange
    debt_token_address = pool_configuration.underlyingAssetToDebtToken(dai)
    debt_token_contract = Contract.from_abi(
        "DebtToken", debt_token_address, DebtToken.abi
    )
    amount = Web3.toWei(100, "ether")

    # act
    debt_token_contract.mint(account, amount, {"from": pool})

    # assert
    assert debt_token_contract.balanceOf(account) == amount


def test_only_pool_can_mint_debt_token(
    add_token, account, pool, pool_configuration, dai
):

    # arrange
    debt_token_address = pool_configuration.underlyingAssetToDebtToken(dai)
    debt_token_contract = Contract.from_abi(
        "DebtToken", debt_token_address, DebtToken.abi
    )
    amount = Web3.toWei(100, "ether")

    # act / assert
    with reverts("caller must be pool"):
        debt_token_contract.mint(account, amount, {"from": account})


def test_burn_debt_token(add_token, account, pool, pool_configuration, dai):

    # arrange
    debt_token_address = pool_configuration.underlyingAssetToDebtToken(dai)
    debt_token_contract = Contract.from_abi(
        "DebtToken", debt_token_address, DebtToken.abi
    )
    amount = Web3.toWei(100, "ether")
    debt_token_contract.mint(account, amount, {"from": pool})

    # act
    debt_token_contract.burn(account, amount, {"from": pool})

    # assert
    assert debt_token_contract.balanceOf(account) == 0


def test_only_pool_can_burn_debt_token(
    add_token, account, pool, pool_configuration, dai
):

    # arrange
    debt_token_address = pool_configuration.underlyingAssetToDebtToken(dai)
    debt_token_contract = Contract.from_abi(
        "DebtToken", debt_token_address, DebtToken.abi
    )
    amount = Web3.toWei(100, "ether")
    debt_token_contract.mint(account, amount, {"from": pool})

    # act / assert
    with reverts("caller must be pool"):
        debt_token_contract.burn(account, amount, {"from": account})


def test_transfer_debt_token_reverts(add_token, account, pool, pool_configuration, dai):

    # arrange
    recepient = get_account(index=2)
    debt_token_address = pool_configuration.underlyingAssetToDebtToken(dai)
    debt_token_contract = Contract.from_abi(
        "DebtToken", debt_token_address, DebtToken.abi
    )
    amount = Web3.toWei(100, "ether")
    debt_token_contract.mint(account, amount, {"from": pool})

    # act / assert
    with reverts("TRANSFER_NOT_SUPPORTED"):
        debt_token_contract.transfer(recepient, amount, {"from": account})


def test_allowance_debt_token_reverts(
    add_token, account, pool, pool_configuration, dai
):

    # arrange
    spender = get_account(index=2)
    debt_token_address = pool_configuration.underlyingAssetToDebtToken(dai)
    debt_token_contract = Contract.from_abi(
        "DebtToken", debt_token_address, DebtToken.abi
    )
    amount = Web3.toWei(100, "ether")
    debt_token_contract.mint(account, amount, {"from": pool})

    # act / assert
    with reverts("ALLOWANCE_NOT_SUPPORTED"):
        debt_token_contract.allowance(account, spender, {"from": account})


def test_approve_debt_token_reverts(add_token, account, pool, pool_configuration, dai):

    # arrange
    spender = get_account(index=2)
    debt_token_address = pool_configuration.underlyingAssetToDebtToken(dai)
    debt_token_contract = Contract.from_abi(
        "DebtToken", debt_token_address, DebtToken.abi
    )
    amount = Web3.toWei(100, "ether")
    debt_token_contract.mint(account, amount, {"from": pool})

    # act / assert
    with reverts("APPROVAL_NOT_SUPPORTED"):
        debt_token_contract.approve(spender, amount, {"from": account})


def test_transfer_from_debt_token_reverts(
    add_token, account, pool, pool_configuration, dai
):

    # arrange
    recipient = get_account(index=2)
    debt_token_address = pool_configuration.underlyingAssetToDebtToken(dai)
    debt_token_contract = Contract.from_abi(
        "DebtToken", debt_token_address, DebtToken.abi
    )
    amount = Web3.toWei(100, "ether")
    debt_token_contract.mint(account, amount, {"from": pool})

    # act / assert
    with reverts("TRANSFER_NOT_SUPPORTED"):
        debt_token_contract.transferFrom(account, recipient, amount, {"from": account})


def test_increase_allowance_debt_token_reverts(
    add_token, account, pool, pool_configuration, dai
):

    # arrange
    spender = get_account(index=2)
    debt_token_address = pool_configuration.underlyingAssetToDebtToken(dai)
    debt_token_contract = Contract.from_abi(
        "DebtToken", debt_token_address, DebtToken.abi
    )
    amount = Web3.toWei(100, "ether")
    debt_token_contract.mint(account, amount, {"from": pool})

    # act / assert
    with reverts("ALLOWANCE_NOT_SUPPORTED"):
        debt_token_contract.increaseAllowance(spender, amount, {"from": account})


def test_decrease_allowance_debt_token_reverts(
    add_token, account, pool, pool_configuration, dai
):

    # arrange
    spender = get_account(index=2)
    debt_token_address = pool_configuration.underlyingAssetToDebtToken(dai)
    debt_token_contract = Contract.from_abi(
        "DebtToken", debt_token_address, DebtToken.abi
    )
    amount = Web3.toWei(100, "ether")
    debt_token_contract.mint(account, amount, {"from": pool})

    # act / assert
    with reverts("ALLOWANCE_NOT_SUPPORTED"):
        debt_token_contract.decreaseAllowance(spender, amount, {"from": account})
