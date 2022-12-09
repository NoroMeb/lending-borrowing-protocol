// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "../interfaces/IXToken.sol";
import "./PriceOracle.sol";
import "./PoolConfiguration.sol";

contract PoolLogic {
    uint256 public constant maxAmountRate = 7500; //in basis points

    PoolConfiguration public poolConfiguration;
    PriceOracle internal priceOracle;

    address internal xToken;
    address internal priceOracleAddress;

    constructor(address _poolConfigurationAddress) public {
        poolConfiguration = PoolConfiguration(_poolConfigurationAddress);
    }

    function getUserBalanceInUSD(address _account, address _underlyingAsset)
        public
        returns (uint256)
    {
        xToken = poolConfiguration.underlyingAssetToXtoken(_underlyingAsset);
        uint256 userBalance = IXToken(xToken).balanceOf(_account);

        priceOracleAddress = poolConfiguration.underlyingAssetToPriceOracle(
            _underlyingAsset
        );
        priceOracle = PriceOracle(priceOracleAddress);

        uint256 assetPrice = priceOracle.getLatestPrice();

        uint256 userBalanceInUSD = userBalance * assetPrice;
        return userBalanceInUSD;
    }

    function getAmountInUSD(uint256 _amount, address _underlyingAsset)
        public
        returns (uint256)
    {
        priceOracleAddress = poolConfiguration.underlyingAssetToPriceOracle(
            _underlyingAsset
        );
        priceOracle = PriceOracle(priceOracleAddress);

        uint256 assetPrice = priceOracle.getLatestPrice();

        uint256 amountInUSD = _amount * assetPrice;

        return amountInUSD;
    }

    function validateBorrow(
        address _account,
        address _underlyingAsset,
        uint256 _amount
    ) public returns (bool) {
        require(_amount > 0, "insufficient amount");
        require(
            poolConfiguration.isAvailable(_underlyingAsset),
            "Token not available"
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
}
