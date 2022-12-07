from scripts.utils import get_account
from brownie import PriceOracle, MockV3Aggregator
from web3 import Web3


def test_get_price(skip_live_testing, mock_v3_aggregator):
    # arrange
    skip_live_testing
    account = get_account()
    decimals = 18
    price = 1000
    price_oracle = PriceOracle.deploy(
        mock_v3_aggregator.address, decimals, {"from": account}
    )

    # act / asssert
    assert price_oracle.getLatestPrice.call() == price
