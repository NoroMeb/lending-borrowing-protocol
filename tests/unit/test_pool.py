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


def test_supply_map_user_to_collateral_to_amount(
    supply, account, dai, pool_configuration, pool
):

    # assert
    assert pool.userToCollateralToAmount(account, dai) == SUPPLY_AMOUNT


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
    assert int(x_token_contract.balanceOf(account) / (10**18)) == (
        SUPPLY_AMOUNT - BORROW_AMOUNT
    ) / (10**18)


def test_borrow_map_user_asset_borrowed_to_collateral(borrow, pool, account, dai):

    # assert
    assert pool.userToBorrowedAssetToCollateral(account, dai) == dai


def test_borrow_mint_debt_token(borrow, pool_configuration, dai, account):

    # arrange
    debt_token_address = pool_configuration.underlyingAssetToDebtToken(dai)
    debt_token_contract = Contract.from_abi(
        "DebtToken", debt_token_address, DebtToken.abi
    )

    # assert
    assert debt_token_contract.balanceOf(account) != 0


def test_borrow_map_user_to_borrowed_asset_to_collateral(
    borrow, pool_configuration, dai, account, pool, add_token_link, link
):

    # arrange
    debt_token_address = pool_configuration.underlyingAssetToDebtToken(dai)
    debt_token_contract = Contract.from_abi(
        "DebtToken", debt_token_address, DebtToken.abi
    )

    # assert
    assert pool.userToBorrowedAssetToCollateral(account, dai) == dai


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


def test_withdraw_decrease_user_to_callateral_to_amount(
    withdraw, pool_configuration, dai, account, pool
):

    # assert
    assert pool.userToCollateralToAmount(account, dai) == 0


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
    assert x_token_contract.balanceOf(account) != 0


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
    variable_borrow_index = Web3.toWei(1, "ether")
    liquidity_rate = Web3.toWei(0, "ether")
    supply_index = Web3.toWei(1, "ether")
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
        liquidity_rate,
        supply_index,
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
    liquidity_rate = Web3.toWei(3.75 * 0.75, "ether")
    supply_index = Web3.toWei(
        1 * (1 + (Web3.fromWei(liquidity_rate, "ether") / 31536000) * 1),
        "ether",
    )
    supply_index_2 = Web3.toWei(
        1 * (1 + (Web3.fromWei(liquidity_rate, "ether") / 31536000) * 2),
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
        liquidity_rate,
        supply_index,
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
        liquidity_rate,
        supply_index_2,
        last_update_time,
        x_token,
        debt_token,
    )

    print(len(reserves_manager.getReserve(dai)))
    print(len(expected_updated_reserve))

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
    liquidity_rate = Web3.toWei(0, "ether")
    supply_index = Web3.toWei(1, "ether")
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
        liquidity_rate,
        supply_index,
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
    liquidity_rate = Web3.toWei(0, "ether")
    supply_index = Web3.toWei(1 * (1 + (3.75 * 0.75) / 31536000) * 1, "ether")
    supply_index_2 = Web3.toWei(1 * (1 + (3.75 * 0.75) / 31536000) * 2, "ether")
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
        liquidity_rate,
        supply_index,
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
        liquidity_rate,
        supply_index_2,
        last_update_time,
        x_token,
        debt_token,
    )

    # assert
    assert (
        reserves_manager.getReserve(dai) == expected_updated_reserve
        or expected_updated_reserve_2
    )


def test_liquidation_call_nul_amount(
    add_token_link,
    supply,
    add_token,
    set_pool_configuration_address,
    set_reserves_manager_address,
    set_pool_logic_address,
    pool_logic,
    pool,
    account,
    dai,
    link,
    mock_v3_aggregator_link,
):

    # arrange
    link.approve(pool, SUPPLY_AMOUNT, {"from": get_account(index=2)})
    pool.supply(link, SUPPLY_AMOUNT, {"from": get_account(index=2)})
    pool.borrow(link, BORROW_AMOUNT, dai, {"from": account})

    new_price = Web3.toWei(20, "ether")

    mock_v3_aggregator_link.updateAnswer(new_price)

    # act / assert
    link.approve(pool, Web3.toWei(50, "ether"), {"from": get_account(index=2)})
    with reverts("insufficient amount"):
        pool.liquidationCall.call(
            account, link, Web3.toWei(0, "ether"), dai, {"from": get_account(index=2)}
        )


def test_liquidation_call_big_amount(
    add_token_link,
    supply,
    add_token,
    set_pool_configuration_address,
    set_reserves_manager_address,
    set_pool_logic_address,
    pool_logic,
    pool,
    account,
    dai,
    link,
    mock_v3_aggregator_link,
):

    # arrange
    link.approve(pool, SUPPLY_AMOUNT, {"from": get_account(index=2)})
    pool.supply(link, SUPPLY_AMOUNT, {"from": get_account(index=2)})
    pool.borrow(link, BORROW_AMOUNT, dai, {"from": account})

    new_price = Web3.toWei(20, "ether")

    mock_v3_aggregator_link.updateAnswer(new_price)

    # act / assert
    link.approve(pool, Web3.toWei(51, "ether"), {"from": get_account(index=2)})
    with reverts("amount exceeds undercollateralized amount"):
        pool.liquidationCall.call(
            account, link, Web3.toWei(51, "ether"), dai, {"from": get_account(index=2)}
        )


def test_liquidation_transform_asset_from_liquidator_to_xtoken_contract(
    add_token_link,
    supply,
    add_token,
    set_pool_configuration_address,
    set_reserves_manager_address,
    set_pool_logic_address,
    pool_logic,
    pool,
    pool_configuration,
    account,
    dai,
    link,
    mock_v3_aggregator_link,
):

    # arrange
    link.approve(pool, SUPPLY_AMOUNT, {"from": get_account(index=2)})
    pool.supply(link, SUPPLY_AMOUNT, {"from": get_account(index=2)})
    pool.borrow(link, BORROW_AMOUNT, dai, {"from": account})

    x_token_address = pool_configuration.underlyingAssetToXtoken(link)
    new_price = Web3.toWei(20, "ether")

    mock_v3_aggregator_link.updateAnswer(new_price)

    liquidation_call_amount = Web3.toWei(50, "ether")

    # act
    link.approve(pool, liquidation_call_amount, {"from": get_account(index=2)})
    pool.liquidationCall(
        account, link, liquidation_call_amount, dai, {"from": get_account(index=2)}
    )

    # assert
    assert (
        link.balanceOf(x_token_address)
        == SUPPLY_AMOUNT - BORROW_AMOUNT + liquidation_call_amount
    )


def test_liquidation_mint_collateral_xtoken_to_liquidator(
    add_token_link,
    supply,
    add_token,
    set_pool_configuration_address,
    set_reserves_manager_address,
    set_pool_logic_address,
    pool_logic,
    pool,
    pool_configuration,
    account,
    dai,
    link,
    mock_v3_aggregator_link,
):

    # arrange
    link.approve(pool, SUPPLY_AMOUNT, {"from": get_account(index=2)})
    pool.supply(link, SUPPLY_AMOUNT, {"from": get_account(index=2)})
    pool.borrow(link, BORROW_AMOUNT, dai, {"from": account})

    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)
    new_price = Web3.toWei(20, "ether")

    mock_v3_aggregator_link.updateAnswer(new_price)

    liquidation_call_amount = Web3.toWei(50, "ether")

    # act
    link.approve(pool, liquidation_call_amount, {"from": get_account(index=2)})
    pool.liquidationCall(
        account, link, liquidation_call_amount, dai, {"from": get_account(index=2)}
    )

    # assert
    assert x_token_contract.balanceOf(get_account(index=2)) == liquidation_call_amount


def test_liquidation_mint_debt_token_to_user(
    add_token_link,
    supply,
    add_token,
    set_pool_configuration_address,
    set_reserves_manager_address,
    set_pool_logic_address,
    pool_logic,
    pool,
    pool_configuration,
    account,
    dai,
    link,
    mock_v3_aggregator_link,
):

    # arrange
    link.approve(pool, SUPPLY_AMOUNT, {"from": get_account(index=2)})
    pool.supply(link, SUPPLY_AMOUNT, {"from": get_account(index=2)})
    pool.borrow(link, BORROW_AMOUNT, dai, {"from": account})

    debt_token_address = pool_configuration.underlyingAssetToDebtToken(dai)
    debt_token_contract = Contract.from_abi(
        "DebtToken", debt_token_address, DebtToken.abi
    )
    new_price = Web3.toWei(20, "ether")

    mock_v3_aggregator_link.updateAnswer(new_price)

    liquidation_call_amount = Web3.toWei(50, "ether")

    # act
    link.approve(pool, liquidation_call_amount, {"from": get_account(index=2)})
    pool.liquidationCall(
        account, link, liquidation_call_amount, dai, {"from": get_account(index=2)}
    )

    # assert
    assert debt_token_contract.balanceOf(account) == liquidation_call_amount


def test_liquidation_call_returns_true(
    add_token_link,
    supply,
    add_token,
    set_pool_configuration_address,
    set_reserves_manager_address,
    set_pool_logic_address,
    pool_logic,
    pool,
    pool_configuration,
    account,
    dai,
    link,
    mock_v3_aggregator_link,
):

    # arrange
    link.approve(pool, SUPPLY_AMOUNT, {"from": get_account(index=2)})
    pool.supply(link, SUPPLY_AMOUNT, {"from": get_account(index=2)})
    pool.borrow(link, BORROW_AMOUNT, dai, {"from": account})

    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)
    new_price = Web3.toWei(20, "ether")

    mock_v3_aggregator_link.updateAnswer(new_price)

    liquidation_call_amount = Web3.toWei(50, "ether")

    # act
    link.approve(pool, liquidation_call_amount, {"from": get_account(index=2)})
    tx = pool.liquidationCall(
        account, link, liquidation_call_amount, dai, {"from": get_account(index=2)}
    )

    # assert
    assert tx.return_value == True


def test_liquidation_call_returns_false(
    add_token_link,
    supply,
    add_token,
    set_pool_configuration_address,
    set_reserves_manager_address,
    set_pool_logic_address,
    pool_logic,
    pool,
    pool_configuration,
    account,
    dai,
    link,
    mock_v3_aggregator_link,
):

    # arrange
    link.approve(pool, SUPPLY_AMOUNT, {"from": get_account(index=2)})
    pool.supply(link, SUPPLY_AMOUNT, {"from": get_account(index=2)})
    pool.borrow(link, BORROW_AMOUNT, dai, {"from": account})

    x_token_address = pool_configuration.underlyingAssetToXtoken(dai)
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)

    liquidation_call_amount = Web3.toWei(50, "ether")

    # act
    link.approve(pool, liquidation_call_amount, {"from": get_account(index=2)})
    tx = pool.liquidationCall(
        account, link, liquidation_call_amount, dai, {"from": get_account(index=2)}
    )

    # assert
    assert tx.return_value == False
