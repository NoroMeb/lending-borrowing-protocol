from scripts.utils import get_account
from brownie import PoolConfiguration, Contract, XToken, exceptions, MockV3Aggregator
import pytest
from web3 import Web3


def test_deploy_pool_configuration(skip_live_testing, pool):
    # arrange
    skip_live_testing
    account = get_account()

    # act
    pool_configuration = PoolConfiguration.deploy(pool.address, {"from": account})

    # assert
    assert pool_configuration.poolAddress() == pool.address

    return pool_configuration


def test_add_token(skip_live_testing, pool, dai, mock_v3_aggregator):
    # arrange
    skip_live_testing
    account = get_account()
    non_owner = get_account(index=2)
    pool_configuration = test_deploy_pool_configuration(skip_live_testing, pool)
    name = "xDai"
    symbol = "xDai"

    # assert

    with pytest.raises(exceptions.VirtualMachineError):
        pool_configuration.addToken(
            name, symbol, dai, mock_v3_aggregator, 18, {"from": non_owner}
        )

    # act
    add_token_tx = pool_configuration.addToken(
        name, symbol, dai, mock_v3_aggregator, 18, {"from": account}
    )
    add_token_tx.wait(1)
    # arrange
    x_token_address = pool_configuration.xtoken()
    x_token_contract = Contract.from_abi("XToken", x_token_address, XToken.abi)

    # assert

    assert x_token_contract.name() == name
    assert x_token_contract.symbol() == symbol
    assert x_token_contract.poolAddress() == pool
    assert x_token_contract.underlyingAsset() == dai
    assert pool_configuration.underlyingAssetToXtoken(dai) == x_token_address
    assert pool_configuration.IsAvailable(dai) == True

    assert (
        pool_configuration.underlyingAssetToPriceOracle(dai)
        == pool_configuration.priceOracle()
    )

    return pool_configuration, x_token_contract
