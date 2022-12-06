from scripts.utils import get_account
from brownie import PriceOracle, MockV3Aggregator
from web3 import Web3


def test_get_price(skip_live_testing):
    # arrange
    account = get_account()
    decimals = 18
    price = 1000
    price_in_wei = Web3.toWei(price, "ether")
    mock_v3_aggregator = MockV3Aggregator.deploy(
        decimals, price_in_wei, {"from": account}
    )
    price_oracle = PriceOracle.deploy({"from": account})

    # act / asssert
    assert (
        price_oracle.getLatestPrice.call(mock_v3_aggregator.address, decimals) == price
    )
