from scripts.utils import get_account
from brownie import (
    PoolConfiguration,
    PoolLogic,
    config,
    network,
)

account = get_account()


def main():
    pool_configuration = PoolConfiguration[-1]
    pool_logic = PoolLogic.deploy(
        pool_configuration,
        {"from": account, "priority_fee": "2 gwei"},
        publish_source=config["networks"][network.show_active()].get("verify"),
    )
    return pool_logic
