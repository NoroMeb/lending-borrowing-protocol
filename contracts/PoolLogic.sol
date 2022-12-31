// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "../interfaces/IXToken.sol";
import "../interfaces/IDebtToken.sol";
import "./PriceOracle.sol";
import "./PoolConfiguration.sol";
import "@ds-math/src/math.sol";

contract PoolLogic is DSMath {
    uint256 public constant maxAmountRate = 7500; //in basis points
    PoolConfiguration public poolConfiguration;

    constructor(address _poolConfigurationAddress) {
        poolConfiguration = PoolConfiguration(_poolConfigurationAddress);
    }

    function getUserBalanceInUSD(address _account, address _underlyingAsset)
        internal
        view
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

    function getUserDebtInUSD(address _account, address _underlyingAsset)
        internal
        view
        returns (uint256)
    {
        address debtToken = poolConfiguration.underlyingAssetToDebtToken(
            _underlyingAsset
        );
        uint256 userDebt = IDebtToken(debtToken).balanceOf(_account);

        address priceOracleAddress = poolConfiguration
            .underlyingAssetToPriceOracle(_underlyingAsset);
        PriceOracle priceOracle = PriceOracle(priceOracleAddress);

        uint256 assetPrice = priceOracle.getLatestPrice();

        uint256 userDebtInUSD = userDebt * assetPrice;
        return userDebtInUSD;
    }

    function getAmountInUSD(uint256 _amount, address _underlyingAsset)
        internal
        view
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
        address _collateral,
        uint256 _amount
    ) public view returns (bool) {
        require(_amount > 0, "Amount must be greater than 0");
        require(
            poolConfiguration.isAvailable(_collateral),
            "token not available"
        );
        address priceOracleAddress = poolConfiguration
            .underlyingAssetToPriceOracle(_collateral);
        PriceOracle priceOracle = PriceOracle(priceOracleAddress);

        uint256 collateralPrice = priceOracle.getLatestPrice();

        uint256 userBalanceInUSD = getUserBalanceInUSD(_account, _collateral);

        uint256 amountInUSD = getAmountInUSD(_amount, _collateral);

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
    function getCollateralAmountToMint(
        address _asset,
        uint256 _amount,
        address _collateral
    ) public view returns (uint256) {
        address priceOracleAddress = poolConfiguration
            .underlyingAssetToPriceOracle(_collateral);
        PriceOracle priceOracle = PriceOracle(priceOracleAddress);

        uint256 collateralPrice = priceOracle.getLatestPrice();
        uint256 amountOfAssetInUSD = getAmountInUSD(_amount, _asset);

        return amountOfAssetInUSD / collateralPrice;
    }

    function validateLiquidation(
        address _user,
        address _asset,
        address _collateral,
        uint256 _collateralAmount
    ) public view returns (bool, uint256) {
        uint256 collateralInUSD = getAmountInUSD(
            _collateralAmount,
            _collateral
        );
        uint256 debtInUSD = getUserDebtInUSD(_user, _asset);

        if (collateralInUSD >= debtInUSD) {
            return (false, 0);
        } else {
            uint256 undercollateralizedAmountInUSD = debtInUSD -
                collateralInUSD;

            address priceOracleAddress = poolConfiguration
                .underlyingAssetToPriceOracle(_collateral);
            PriceOracle priceOracle = PriceOracle(priceOracleAddress);

            uint256 assetPrice = priceOracle.getLatestPrice();

            return (true, undercollateralizedAmountInUSD / assetPrice);
        }
    }
}
