from scripts.utils import get_account
from brownie import reverts, Contract, XToken
from web3 import Web3
from conftest import SUPPLY_AMOUNT


def test_set_pool_configuration_address(
    set_pool_configuration_address, pool, pool_configuration
):

    # assert
    assert pool.poolConfiguration() == pool_configuration


def test_only_owner_can_set_pool_configuration_address(pool, pool_configuration):

    # arrange
    non_owner = get_account(index=2)

    # act / assert
    with reverts():
        pool.setPoolConfigurationAddress(pool_configuration, {"from": non_owner})


def test_set_pool_logic_address(set_pool_logic_address, pool, pool_logic):

    # assert
    assert pool.poolLogic() == pool_logic


def test_only_owner_can_set_pool_logic_address(pool, pool_logic):

    # arrange
    non_owner = get_account(index=2)

    # act / assert
    with reverts():
        pool.setPoolConfigurationAddress(pool_logic, {"from": non_owner})


def test_supply_null_amount(
    set_pool_configuration_address, add_token, account, pool, dai
):

    # act / assert
    with reverts("insufficient amount"):
        pool.supply(dai, 0, {"from": account})


def test_supply_non_available_token(
    set_pool_configuration_address, add_token, account, pool, link
):

    # arrange
    amount = Web3.toWei(100, "ether")
    link.approve(pool, amount, {"from": account})

    # act / assert
    with reverts("Token not available"):
        pool.supply(link, amount, {"from": account})


def test_supply_transfer_funds_from_supplier_account_to_xtoken(
    account_initial_dai_balance, account, supply, dai, pool_configuration
):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)

    # assert
    assert dai.balanceOf(x_token_address) == SUPPLY_AMOUNT
    assert dai.balanceOf(account) == account_initial_dai_balance - SUPPLY_AMOUNT


def test_supply_mint_xtoken_to_supplier(supply, account, dai, pool_configuration):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)

    # assert
    assert x_token_contract.balanceOf(account) == SUPPLY_AMOUNT


def test_withdraw_null_amount(supply, pool, account, dai):

    # act / assert
    with reverts("Amount must be greater than 0"):
        pool.withdraw(dai, 0, {"from": account})


def test_withdraw_non_available_token(supply, pool, account, link):

    # arrange
    amount = Web3.toWei(100, "ether")
    with reverts("Token not available"):
        pool.withdraw(link, amount, {"from": account})


def test_withdraw_with_no_funds_supplied(
    add_token, set_pool_configuration_address, pool, account, dai
):

    # arrange
    amount = Web3.toWei(100, "ether")
    with reverts("Don't have any funds here"):
        pool.withdraw(dai, amount, {"from": account})


def test_withdraw_transfer_funds_from_xtoken_to_withdrawer(
    withdraw, dai, pool_configuration, account, account_initial_dai_balance
):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)

    # assert
    assert dai.balanceOf(x_token_address) == 0
    assert dai.balanceOf(account) == account_initial_dai_balance


def test_withdraw_burn_withdrawer_xtoken(withdraw, dai, pool_configuration, account):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)

    # assert
    assert x_token_contract.balanceOf(account) == 0


def test_borrow_invalid_amount(supply, dai, pool, set_pool_logic_address, account):

    # arrange
    amount = Web3.toWei(76, "ether")

    # act
    return_value = pool.borrow.call(dai, amount, {"from": account})

    # assert
    assert return_value == 0


def test_borrow_valid_amount(supply, dai, pool, set_pool_logic_address, account):

    # arrange
    amount = Web3.toWei(75, "ether")

    # act
    return_value = pool.borrow.call(dai, amount, {"from": account})

    # assert
    assert return_value == amount


def test_borrow_transfer_funds_from_xtoken_to_borrower(borrow, pool_configuration, dai):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    expected = Web3.toWei(25, "ether")  # 100 supplied - 75 borrowed = 25

    # assert
    assert dai.balanceOf(x_token_address) == expected


def test_borrow_burn_amount_of_xtoken(borrow, pool_configuration, dai, account):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)
    expected = Web3.toWei(25, "ether")

    # assert
    assert x_token_contract.balanceOf(account) == expected
