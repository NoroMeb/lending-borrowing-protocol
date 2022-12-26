from brownie import DebtToken, Contract, reverts, DebtToken, chain
from web3 import Web3
from scripts.utils import get_account
from conftest import BORROW_AMOUNT


def test_debt_token_constructor(account, dai, pool, reserves_manager):

    # arrange
    name = "debtTEST"
    symbol = "debtTEST"
    pool_address = pool

    # act
    debt_token = DebtToken.deploy(
        name, symbol, dai, pool_address, reserves_manager, {"from": account}
    )

    # assert
    assert debt_token.name() == name
    assert debt_token.symbol() == name
    assert debt_token.poolAddress() == pool_address


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


def test_debt_token_balance_of(
    add_token, borrow, pool_configuration, dai, account, reserves_manager
):

    # arrange
    debt_token_address = pool_configuration.underlyingAssetToDebtToken(dai)
    debt_token_contract = Contract.from_abi(
        "DebtToken", debt_token_address, DebtToken.abi
    )

    chain.sleep(10)
    chain.mine(1)
    expected_debt_token_balance = Web3.fromWei(
        BORROW_AMOUNT, "ether"
    ) * reserves_manager.getVariableBorrowIndexSinceLastUpdate(dai)

    # assert
    assert debt_token_contract.balanceOf(account) == expected_debt_token_balance
