from scripts.utils import get_account
from brownie import (
    Pool,
    config,
    network,
    PoolConfiguration,
    PoolLogic,
    ReservesManager,
    MockDai,
    Contract,
)
from web3 import Web3

account = get_account()


def main():
    repay()


def deploy_pool():
    pool = Pool.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify"),
    )

    return pool


def set_pool_configuration_address():
    pool_configuration = PoolConfiguration[-1]
    pool = Pool[-1]
    pool.setPoolConfigurationAddress(
        pool_configuration, {"from": account, "priority_fee": "2 gwei"}
    )


def set_pool_logic_address():
    pool_logic = PoolLogic[-1]
    pool = Pool[-1]
    pool.setPoolLogicAddress(pool_logic, {"from": account, "priority_fee": "2 gwei"})


def set_reserves_manager_address():
    reserves_manager = ReservesManager[-1]
    pool = Pool[-1]
    pool.setReservesManagerAddress(
        reserves_manager, {"from": account, "priority_fee": "2 gwei"}
    )


def supply_dai():
    account_1 = get_account()
    account_2 = get_account(num=2)
    pool = Pool[-1]
    dai = MockDai[-1]
    amount_to_supply = Web3.toWei(1000, "ether")
    dai.approve(pool, amount_to_supply, {"from": account, "priority_fee": "2 gwei"})
    pool.supply(dai, amount_to_supply, {"from": account, "priority_fee": "2 gwei"})


def supply_link():
    account_1 = get_account()
    account_2 = get_account(num=2)
    pool = Pool[-1]
    link_address = config["networks"][network.show_active()].get("link_token")
    link_contract = Contract.from_explorer(link_address)
    amount_to_supply = Web3.toWei(10, "ether")
    link_contract.approve(
        pool, amount_to_supply, {"from": account_2, "priority_fee": "2 gwei"}
    )
    pool.supply(
        link_address, amount_to_supply, {"from": account_2, "priority_fee": "2 gwei"}
    )


def borrow():
    account_1 = get_account()
    account_2 = get_account(num=2)
    pool = Pool[-1]
    dai = MockDai[-1]
    link_address = config["networks"][network.show_active()].get("link_token")
    link_contract = Contract.from_explorer(link_address)
    amount_to_borrow = Web3.toWei(10, "ether")
    tx = pool.borrow(dai, amount_to_borrow, link_address, {"from": account_2})


def repay():
    account_2 = get_account(num=2)
    pool = Pool[-1]
    dai = MockDai[-1]
    link_address = config["networks"][network.show_active()].get("link_token")
    link_contract = Contract.from_explorer(link_address)
    amount_to_repay = Web3.toWei(10, "ether")
    dai.approve(pool, amount_to_repay, {"from": account_2, "priority_fee": "2 gwei"})
    tx = pool.repay(dai, amount_to_repay, {"from": account_2})
