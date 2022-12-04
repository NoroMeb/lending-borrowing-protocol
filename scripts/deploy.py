from scripts.utils import get_account
from brownie import PoolConfiguration, MockDai, Pool, Contract, XToken
from web3 import Web3


def main():
    account = get_account()
    amount = Web3.toWei(100, "ether")
    dai = MockDai.deploy({"from": account})
    pool = Pool.deploy({"from": account})
    pool_configuration = PoolConfiguration.deploy(pool.address, {"from": account})
    pool.setPoolConfigurationAddress(pool_configuration.address, {"from": account})
    add_token_tx = pool_configuration.addToken(dai, "xDAI", "xDAI")
    add_token_tx.wait(1)
    approve_tx = dai.approve(pool, amount, {"from": account})
    supply_tx = pool.supply(dai, amount, {"from": account})
    supply_tx.wait(1)

    # test

    x_dai_address = pool_configuration.getXToken(dai)
    print("=====================================")
    print("xDAI contract balance :")
    print(dai.balanceOf(x_dai_address))
    print("=====================================")
    x_dai_contract = Contract.from_abi("XToken", x_dai_address, XToken.abi)
    print("=====================================")
    print("account balance :")
    print(x_dai_contract.balanceOf(account))
    print("=====================================")
