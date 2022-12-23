// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "./../PoolConfiguration.sol";

contract PoolConfigurationMock is PoolConfiguration {
    constructor(address _poolAddress) PoolConfiguration(_poolAddress) {}

    function getXToken() public view returns (XToken) {
        return xtoken;
    }

    function getDebtToken() public view returns (DebtToken) {
        return debtToken;
    }

    function getPriceOracle() public view returns (PriceOracle) {
        return priceOracle;
    }

    function _initReserve(
        address _underlyingAsset,
        uint256 _baseVariableBorrowRate,
        uint256 _interestRateSlope
    ) public {
        super.initReserve(
            _underlyingAsset,
            _baseVariableBorrowRate,
            _interestRateSlope
        );
    }
}
