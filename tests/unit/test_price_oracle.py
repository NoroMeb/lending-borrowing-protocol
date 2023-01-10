from conftest import PRICE


def test_price_oracle_constructor(price_oracle, mock_v3_aggregator, skip_live_testing):

    # assert
    assert price_oracle.priceFeed() == mock_v3_aggregator


def test_get_latest_price(price_oracle, skip_live_testing):

    # assert
    assert price_oracle.getLatestPrice.call() == PRICE
