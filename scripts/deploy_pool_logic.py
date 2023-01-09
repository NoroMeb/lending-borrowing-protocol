from scripts.utils import get_account
from brownie import PoolConfiguration, PoolLogic, config, network, MockDai, Contract
from web3 import Web3

account = get_account()
account_2 = get_account(num=2)


def main():
    get_amount_in_usd()


def deploy_pool_logic():
    pool_configuration = PoolConfiguration[-1]
    pool_logic = PoolLogic.deploy(
        pool_configuration,
        {"from": account, "priority_fee": "2 gwei"},
        publish_source=config["networks"][network.show_active()].get("verify"),
    )
    return pool_logic


def validate_borrow():
    pool_logic = PoolLogic[-1]
    dai = MockDai[-1]
    link_address = config["networks"][network.show_active()].get("link_token")
    link_contract = Contract.from_explorer(link_address)
    amount = Web3.toWei(100, "ether")
    pool_logic.validateBorrow(account_2, dai, amount, link_address)


def get_user_balance_in_usd():
    pool_logic = PoolLogic[-1]
    dai = MockDai[-1]
    link_address = config["networks"][network.show_active()].get("link_token")
    print(pool_logic.getUserBalanceInUSD(account_2, link_address))


def get_amount_in_usd():
    pool_logic = PoolLogic[-1]
    dai = MockDai[-1]
    link_address = config["networks"][network.show_active()].get("link_token")
    amount = Web3.toWei(10, "ether")
    print(pool_logic.getAmountInUSD(amount, link_address))
