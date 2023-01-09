from scripts.utils import get_account
from brownie import PoolConfiguration, Pool, config, network, ReservesManager, MockDai
from web3 import Web3

account = get_account()


def main():
    add_link_token()


def deploy_pool_configuration():
    pool = Pool[-1]
    pool_configuration = PoolConfiguration.deploy(
        pool,
        {"from": account, "priority_fee": "2 gwei"},
        publish_source=config["networks"][network.show_active()].get("verify"),
    )
    return pool_configuration


def set_reserves_manager_contract():
    reserves_manager = ReservesManager[-1]
    pool_configuration = PoolConfiguration[-1]
    pool_configuration.setReserveManagerContract(
        reserves_manager, {"from": account, "priority_fee": "2 gwei"}
    )


def add_dai_token():
    pool_configuration = PoolConfiguration[-1]
    name = "DAI"
    symbol = "DAI"
    underlying_asset = MockDai[-1]
    price_feed_address = config["networks"][network.show_active()].get(
        "dai_usd_price_feed"
    )
    decimals = 18
    base_variable_borrow_rate = Web3.toWei(0, "ether")
    interest_rate_slope = Web3.toWei(5, "ether")
    pool_configuration.addToken(
        name,
        symbol,
        underlying_asset,
        price_feed_address,
        decimals,
        base_variable_borrow_rate,
        interest_rate_slope,
        {"from": account, "priority_fee": "2 gwei"},
    )


def add_link_token():
    pool_configuration = PoolConfiguration[-1]
    name = "LINK"
    symbol = "LINK"
    underlying_asset = config["networks"][network.show_active()].get("link_token")
    price_feed_address = config["networks"][network.show_active()].get(
        "link_usd_price_feed"
    )
    decimals = 18
    base_variable_borrow_rate = Web3.toWei(0, "ether")
    interest_rate_slope = Web3.toWei(5, "ether")
    pool_configuration.addToken(
        name,
        symbol,
        underlying_asset,
        price_feed_address,
        decimals,
        base_variable_borrow_rate,
        interest_rate_slope,
        {"from": account, "priority_fee": "2 gwei"},
    )
