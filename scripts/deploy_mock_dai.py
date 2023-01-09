from scripts.utils import get_account
from brownie import (
    MockDai,
    config,
    network,
    config,
)

account = get_account()


def main():
    deploy_mock_dai()

def deploy_mock_dai():
    mock_dai = MockDai.deploy(
        {"from": account, "priority_fee": "1 gwei"},
        publish_source=config["networks"][network.show_active()].get("verify"),
    )
    return mock_dai
