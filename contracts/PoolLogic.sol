// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "../interfaces/IXToken.sol";
import "./PriceOracle.sol";
import "./PoolConfiguration.sol";

contract PoolLogic {
    uint256 public constant maxAmountRate = 7500; //in basis points
    PoolConfiguration public poolConfiguration;

    constructor(address _poolConfigurationAddress) {
        poolConfiguration = PoolConfiguration(_poolConfigurationAddress);
    }

    function getUserBalanceInUSD(address _account, address _underlyingAsset)
        internal
        returns (uint256)
    {
        address xToken = poolConfiguration.underlyingAssetToXtoken(
            _underlyingAsset
        );
        uint256 userBalance = IXToken(xToken).balanceOf(_account);

        address priceOracleAddress = poolConfiguration
            .underlyingAssetToPriceOracle(_underlyingAsset);
        PriceOracle priceOracle = PriceOracle(priceOracleAddress);

        uint256 assetPrice = priceOracle.getLatestPrice();

        uint256 userBalanceInUSD = userBalance * assetPrice;
        return userBalanceInUSD;
    }

    function getAmountInUSD(uint256 _amount, address _underlyingAsset)
        internal
        returns (uint256)
    {
        address priceOracleAddress = poolConfiguration
            .underlyingAssetToPriceOracle(_underlyingAsset);
        PriceOracle priceOracle = PriceOracle(priceOracleAddress);

        uint256 assetPrice = priceOracle.getLatestPrice();

        uint256 amountInUSD = _amount * assetPrice;

        return amountInUSD;
    }

    function validateBorrow(
        address _account,
        address _underlyingAsset,
        uint256 _amount
    ) public returns (bool) {
        require(_amount > 0, "Amount must be greater than 0");
        require(
            poolConfiguration.isAvailable(_underlyingAsset),
            "token not available"
        );

        uint256 userBalanceInUSD = getUserBalanceInUSD(
            _account,
            _underlyingAsset
        );

        uint256 amountInUSD = getAmountInUSD(_amount, _underlyingAsset);

        uint256 maxAmountInUSD = (userBalanceInUSD / 10000) * maxAmountRate;

        if (amountInUSD <= maxAmountInUSD) {
            return true;
        } else {
            return false;
        }
    }

    function validateWithdraw(
        address _account,
        address _underlyingAsset,
        uint256 _amount
    ) public view returns (bool) {
        require(_amount > 0, "Amount must be greater than 0");
        require(
            poolConfiguration.isAvailable(_underlyingAsset),
            "token not available"
        );

        address xtoken = poolConfiguration.underlyingAssetToXtoken(
            _underlyingAsset
        );
        uint256 userBalance = IXToken(xtoken).balanceOf(_account);

        if (_amount > userBalance) {
            return false;
        } else {
            return true;
        }
    }
}
