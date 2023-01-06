from brownie import network, accounts, config

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache"]


def get_account(index=None, id=None, num=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    if network.show_active() in config["networks"] and not num:
        return accounts.add(config["wallets"]["from_key"])
    if network.show_active() in config["networks"] and num == 2:
        return accounts.add(config["wallets"]["from_key_2"])
    return None
