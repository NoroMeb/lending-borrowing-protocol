// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "./../PoolConfiguration.sol";

contract PoolConfigurationMock is PoolConfiguration {
    constructor(address _poolAddress) public PoolConfiguration(_poolAddress) {}

    function getXToken() public returns (XToken) {
        return xtoken;
    }

    function getPriceOracle() public returns (PriceOracle) {
        return priceOracle;
    }
}
