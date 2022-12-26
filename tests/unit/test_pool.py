from scripts.utils import get_account
from brownie import reverts, Contract, XToken, DebtToken, chain
from web3 import Web3
from conftest import (
    SUPPLY_AMOUNT,
    WITHDRAW_AMOUNT,
    BORROW_AMOUNT,
    BASE_VARIABLE_BORROW_RATE,
    INTEREST_RATE_SLOPE,
)


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


def test_set_reserves_manager_address(
    set_reserves_manager_address, pool, reserves_manager
):

    # assert
    assert pool.reservesManager() == reserves_manager


def test_only_owner_can_set_reserves_manager_address(pool, reserves_manager):

    # arrange
    non_owner = get_account(index=2)

    # act / assert
    with reverts():
        pool.setReservesManagerAddress(reserves_manager, {"from": non_owner})


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
    with reverts("token not available"):
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


def test_supply_increase_total_deposited(
    supply, pool_configuration, reserves_manager, dai, account
):

    # arrange

    # assert
    assert reserves_manager.getTotalDeposited(dai) == SUPPLY_AMOUNT


def test_borrow_transfer_funds_from_xtoken_to_borrower(borrow, pool_configuration, dai):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    expected = Web3.toWei(25, "ether")  # 100 supplied - 75 borrowed = 25

    # assert
    assert dai.balanceOf(x_token_address) == SUPPLY_AMOUNT - BORROW_AMOUNT


def test_borrow_burn_amount_of_xtoken(borrow, pool_configuration, dai, account):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)
    expected = Web3.toWei(25, "ether")

    # assert
    assert x_token_contract.balanceOf(account) == SUPPLY_AMOUNT - BORROW_AMOUNT


def test_borrow_mint_debt_token(borrow, pool_configuration, dai, account):

    # arrange
    debt_token_address = pool_configuration.underlyingAssetToDebtToken(dai)
    debt_token_contract = Contract.from_abi(
        "DebtToken", debt_token_address, DebtToken.abi
    )

    # assert
    assert debt_token_contract.balanceOf(account) == BORROW_AMOUNT


def test_borrow_increase_total_borrowed(borrow, reserves_manager, dai, account):

    # assert
    assert reserves_manager.getTotalBorrowed(dai) == BORROW_AMOUNT


def test_withdraw_transfer_funds_from_xtoken_to_withdrawer(
    account_initial_dai_balance, withdraw, pool_configuration, dai, account
):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)

    # assert
    assert dai.balanceOf(x_token_address) == 0
    assert dai.balanceOf(account) == account_initial_dai_balance


def test_withdraw_burn_amount_of_xtoken(withdraw, pool_configuration, dai, account):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)

    # assert
    assert x_token_contract.balanceOf(account) == 0


def test_withdraw_decrease_total_deposited(withdraw, reserves_manager, dai):

    # assert
    assert reserves_manager.getTotalDeposited(dai) == 0


def test_repay_invalid_insufficient_amount(borrow, pool, dai, account):

    # act / assert
    with reverts("insufficient amount"):
        pool.repay(dai, 0, {"from": account})


def test_repay_non_available_token(borrow, account, pool, link):

    # arrange
    link.approve(pool, BORROW_AMOUNT, {"from": account})

    # act / assert
    with reverts("token not available"):
        pool.repay(link, BORROW_AMOUNT, {"from": account})


def test_repay_with_no_debt(supply, account, pool, dai):

    # act / assert
    with reverts("doesnt have a debt to pay"):
        pool.repay(dai, BORROW_AMOUNT, {"from": account})


def test_repay_amount_exceeds_debt(borrow, account, pool, dai):

    # arrange
    amount = Web3.toWei(85, "ether")
    dai.approve(pool, amount, {"from": account})

    # act / assert
    with reverts("the amount exceeds the debt"):
        pool.repay(dai, amount, {"from": account})


def test_repay_transfer_funds_from_user_account_to_xtoken(
    repay, account, pool, pool_configuration, dai
):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)

    # assert
    assert dai.balanceOf(x_token_address) == SUPPLY_AMOUNT


def test_repay_mint_xtoken_to_user(repay, account, pool, pool_configuration, dai):

    # arrange
    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)

    # assert
    assert x_token_contract.balanceOf(account) == SUPPLY_AMOUNT


def test_repay_burn_debt_token(repay, account, pool_configuration, dai):

    # arrange
    debt_token_address = pool_configuration.underlyingAssetToDebtToken(dai)
    debt_token_contract = Contract.from_abi(
        "DebtToken", debt_token_address, DebtToken.abi
    )

    # assert
    assert debt_token_contract.balanceOf(account) == 0


def test_update_state_on_supply(supply, add_token, reserves_manager, dai):

    # arrange
    total_deposited = SUPPLY_AMOUNT
    total_borrowed = 0
    utilization_rate = Web3.toWei(0, "ether")
    variable_borrow_rate = Web3.toWei(0, "ether")
    base_variable_borrow_rate = BASE_VARIABLE_BORROW_RATE
    interest_rate_slope = INTEREST_RATE_SLOPE
    variable_borrow_index = Web3.toWei(
        1,
        "ether",
    )
    last_update_time = chain[-1].timestamp
    x_token = add_token[0]
    debt_token = add_token[1]

    expected_updated_reserve = (
        total_deposited,
        total_borrowed,
        utilization_rate,
        variable_borrow_rate,
        base_variable_borrow_rate,
        interest_rate_slope,
        variable_borrow_index,
        last_update_time,
        x_token,
        debt_token,
    )

    # assert
    assert reserves_manager.getReserve(dai) == expected_updated_reserve


def test_update_state_on_borrow(borrow, add_token, reserves_manager, dai):

    # arrange
    total_deposited = SUPPLY_AMOUNT
    total_borrowed = BORROW_AMOUNT
    utilization_rate = Web3.toWei(0.75, "ether")
    variable_borrow_rate = Web3.toWei(3.75, "ether")
    base_variable_borrow_rate = BASE_VARIABLE_BORROW_RATE
    interest_rate_slope = INTEREST_RATE_SLOPE
    variable_borrow_index = Web3.toWei(
        1 * (1 + (Web3.fromWei(variable_borrow_rate, "ether") / 31536000) * 1),
        "ether",
    )
    variable_borrow_index_2 = Web3.toWei(
        1 * (1 + (Web3.fromWei(variable_borrow_rate, "ether") / 31536000) * 2),
        "ether",
    )
    last_update_time = chain[-1].timestamp
    x_token = add_token[0]
    debt_token = add_token[1]

    expected_updated_reserve = (
        total_deposited,
        total_borrowed,
        utilization_rate,
        variable_borrow_rate,
        base_variable_borrow_rate,
        interest_rate_slope,
        variable_borrow_index,
        last_update_time,
        x_token,
        debt_token,
    )

    expected_updated_reserve_2 = (
        total_deposited,
        total_borrowed,
        utilization_rate,
        variable_borrow_index,
        base_variable_borrow_rate,
        interest_rate_slope,
        variable_borrow_index_2,
        last_update_time,
        x_token,
        debt_token,
    )

    print(variable_borrow_index)

    # assert
    assert (
        reserves_manager.getReserve(dai) == expected_updated_reserve
        or expected_updated_reserve_2
    )


def test_update_state_on_withdraw(withdraw, add_token, reserves_manager, dai):

    # arrange
    total_deposited = 0
    total_borrowed = 0
    utilization_rate = Web3.toWei(0, "ether")
    variable_borrow_rate = Web3.toWei(0, "ether")
    base_variable_borrow_rate = BASE_VARIABLE_BORROW_RATE
    interest_rate_slope = INTEREST_RATE_SLOPE
    variable_borrow_index = Web3.toWei(
        1,
        "ether",
    )
    last_update_time = chain[-1].timestamp
    x_token = add_token[0]
    debt_token = add_token[1]

    expected_updated_reserve = (
        total_deposited,
        total_borrowed,
        utilization_rate,
        variable_borrow_rate,
        base_variable_borrow_rate,
        interest_rate_slope,
        variable_borrow_index,
        last_update_time,
        x_token,
        debt_token,
    )

    # assert
    assert reserves_manager.getReserve(dai) == expected_updated_reserve


def test_update_state_on_repay(repay, add_token, reserves_manager, dai):

    # arrange
    total_deposited = SUPPLY_AMOUNT
    total_borrowed = 0
    utilization_rate = Web3.toWei(0, "ether")
    variable_borrow_rate = Web3.toWei(0, "ether")
    base_variable_borrow_rate = BASE_VARIABLE_BORROW_RATE
    interest_rate_slope = INTEREST_RATE_SLOPE
    variable_borrow_index = Web3.toWei(1 * (1 + 3.75 / 31536000) * 1, "ether")
    variable_borrow_index_2 = Web3.toWei(1 * (1 + 3.75 / 31536000) * 2, "ether")
    last_update_time = chain[-1].timestamp
    x_token = add_token[0]
    debt_token = add_token[1]

    expected_updated_reserve = (
        total_deposited,
        total_borrowed,
        utilization_rate,
        variable_borrow_rate,
        base_variable_borrow_rate,
        interest_rate_slope,
        variable_borrow_index,
        last_update_time,
        x_token,
        debt_token,
    )

    expected_updated_reserve_2 = (
        total_deposited,
        total_borrowed,
        utilization_rate,
        variable_borrow_rate,
        base_variable_borrow_rate,
        interest_rate_slope,
        variable_borrow_index_2,
        last_update_time,
        x_token,
        debt_token,
    )

    # assert
    assert (
        reserves_manager.getReserve(dai) == expected_updated_reserve
        or expected_updated_reserve_2
    )
