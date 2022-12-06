from scripts.utils import get_account
from brownie import PoolConfiguration, MockDai, Pool, Contract, XToken, PoolLogic
from web3 import Web3


def main():

    account = get_account()
    pool_logic = PoolLogic[-1]
    price = pool_logic.getLatestPrice.call(
        "0x779877A7B0D9E8603169DdbD7836e478b4624789", 18, {"from": account}
    )

    print("=================================")
    print(price)
    print("=================================")
