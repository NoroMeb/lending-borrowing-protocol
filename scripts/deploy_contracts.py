from scripts.utils import get_account
from brownie import (
    PoolConfiguration,
    Pool,
    PoolLogic,
    ReservesManager,
    config,
    network,
    Contract,
    MockDai,
)

account = get_account()


def main():
    deploy_reserves_manager()


def deploy_pool():
    pool = Pool.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify"),
    )
    return pool


def deploy_pool_configuration():
    pool = deploy_pool()
    pool_configuration = PoolConfiguration.deploy(
        pool,
        {"from": account, "priority_fee": "2 gwei"},
        publish_source=config["networks"][network.show_active()].get("verify"),
    )
    return pool_configuration


def deploy_pool_logic():
    pool_configuration = deploy_pool_configuration()
    pool_logic = PoolLogic.deploy(
        pool_configuration,
        {"from": account, "priority_fee": "2 gwei"},
        publish_source=config["networks"][network.show_active()].get("verify"),
    )
    return pool_logic


def deploy_reserves_manager():
    pool_configuration = deploy_pool_configuration()
    pool = deploy_pool()
    reserves_manager = ReservesManager.deploy(
        pool_configuration,
        pool,
        {"from": account, "priority_fee": "2 gwei"},
        publish_source=config["networks"][network.show_active()].get("verify"),
    )
    return reserves_manager


def deploy_mock_dai():
    mock_dai = MockDai.deploy(
        {"from": account, "priority_fee": "1 gwei"},
        publish_source=config["networks"][network.show_active()].get("verify"),
    )
    return mock_dai
