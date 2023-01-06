from scripts.utils import get_account
from brownie import (
    Pool,
    config,
    network,
    PoolConfiguration,
    PoolLogic,
    ReservesManager,
    MockDai,
)
from web3 import Web3

account = get_account()


def main():
    supply_dai()


def deploy():
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
