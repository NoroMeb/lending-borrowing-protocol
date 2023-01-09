from scripts.utils import get_account
from brownie import (
    PoolConfiguration,
    Pool,
    ReservesManager,
    config,
    network,
)

account = get_account()


def main():
    deploy_reserves_manager()

def deploy_reserves_manager():
    pool_configuration = PoolConfiguration[-1]
    pool = Pool[-1]
    reserves_manager = ReservesManager.deploy(
        pool_configuration,
        pool,
        {"from": account, "priority_fee": "2 gwei"},
        publish_source=config["networks"][network.show_active()].get("verify"),
    )
    return reserves_manager