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
from scripts.utils import get_account
from scripts.deploy_pool import deploy_pool
from scripts.deploy_pool_configuration import (
    deploy_pool_configuration,
    add_dai_token,
    add_link_token,
)
from scripts.deploy_pool_logic import deploy_pool_logic
from scripts.deploy_reserves_manager import deploy_reserves_manager
from scripts.deploy_mock_dai import deploy_mock_dai


def main():

    # account
    account = get_account()

    # deploy contracts
    pool = deploy_pool()
    pool_configuration = deploy_pool_configuration()
    pool_logic = deploy_pool_logic()
    reserves_manager = deploy_reserves_manager()
    mock_dai = deploy_mock_dai()

    # set addresses
    pool.setPoolConfigurationAddress(
        pool_configuration, {"from": account, "priority_fee": "2 gwei"}
    )
    pool.setPoolLogicAddress(pool_logic, {"from": account, "priority_fee": "2 gwei"})
    pool.setReservesManagerAddress(
        reserves_manager, {"from": account, "priority_fee": "2 gwei"}
    )
    pool_configuration.setReserveManagerContract(
        reserves_manager, {"from": account, "priority_fee": "2 gwei"}
    )

    # add tokens
    add_dai_token()
    add_link_token()
