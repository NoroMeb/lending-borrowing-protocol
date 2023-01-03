// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "../interfaces/IXToken.sol";
import "../interfaces/IDebtToken.sol";
import "./PriceOracle.sol";
import "./PoolConfiguration.sol";
import "@ds-math/src/math.sol";

/**
 * @author  . MEBARKIA Abdenour
 * @title   . PoolLogic
 * @dev     . validate some end-user functions in the Pool contract
 */

contract PoolLogic is DSMath {
    uint256 public constant maxAmountRate = 7500; //in basis points
    PoolConfiguration public poolConfiguration;

    constructor(address _poolConfigurationAddress) {
        poolConfiguration = PoolConfiguration(_poolConfigurationAddress);
    }

    /**
     * @dev     . get the user xToken balance in USD
     * @param   _account  . the user's address
     * @param   _underlyingAsset  . the asset underlying asset's xToken
     * @return  uint256  . returns user xToken balance in USD
     */
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

    /**
     * @dev     . get the user debtToken balance in USD
     * @param   _account  . the user's address
     * @param   _underlyingAsset  . the asset underlying asset's xToken
     * @return  uint256  . returns user debtToken balance in USD
     */
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

    /**
     * @dev     . get an amount of an underlying asset price in USD
     * @param   _amount  . the amount to get its price
     * @param   _underlyingAsset  . the underlying asset address
     * @return  uint256  . price in USD
     */
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

    /**
     * @dev     . tells if user is legitimate to borrow
     * @param   _account  . the address of the user who wants to borrow
     * @param   _asset  . The address of the underlying asset to borrow
     * @param   _amount  . The amount to be borrowed
     * @param   _collateral  . he address of the underlying asset to set as collateral
     * @return  bool  . success boolian
     * @return  uint256  . the amount borrowed if the user is legitimate to borrow otherwise it returns 0
     */
    function validateBorrow(
        address _account,
        address _asset,
        uint256 _amount,
        address _collateral
    ) public view returns (bool, uint256) {
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

        uint256 amountInUSD = getAmountInUSD(_amount, _asset);

        uint256 amountOfCollateral = amountInUSD / collateralPrice;

        uint256 maxAmountInUSD = (userBalanceInUSD / 10000) * maxAmountRate;

        if (amountInUSD <= maxAmountInUSD) {
            return (true, amountOfCollateral);
        } else {
            return (false, 0);
        }
    }

    /**
     * @dev     . tells if user is legitimate to withdraw
     * @param   _account  . the address of the user who wants to withdraw
     * @param   _underlyingAsset  . The address of the underlying asset to withdraw
     * @param   _amount  . The amount to be withdrawn
     * @return  bool  . legitimacy boolian
     */
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

    /**
     * @dev     . get the collateral amount to mint depending on an amount of asset
     * @param   _asset  . address of the asset
     * @param   _amount  . the amount of the asset
     * @param   _collateral  . the address of the collateral to mint
     * @return  uint256  . collateral amount
     */
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

    /**
     * @dev     . tells if user is legitimate to liquidate a non-healthy position collateral-wise
     * @param   _user  . The address of the borrower getting liquidated
     * @param   _asset  . The address of the underlying borrowed asset to be repaid with the liquidation
     * @param   _collateral  . The address of the underlying asset used as collateral, to receive as result of the liquidation
     * @param   _collateralAmount  . the amount of collateral borrower hass
     * @return  bool  . legitimacy boolian
     * @return  uint256  . the amount undercollateralized
     */
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
