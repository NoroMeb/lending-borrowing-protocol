// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "./../PoolConfiguration.sol";
import "./PriceOracleMock.sol";

contract PoolConfigurationMock is PoolConfiguration {
    constructor(address _poolAddress) PoolConfiguration(_poolAddress) {}

    function addToken(
        string memory _name,
        string memory _symbol,
        address _underlyingAsset,
        address _priceFeedAddress,
        uint256 _decimals,
        uint256 _baseVariableBorrowRate,
        uint256 _interestRateSlope
    )
        external
        override
        onlyOwner
        returns (
            address,
            address,
            address
        )
    {
        xtoken = new XToken(
            string.concat("x", _name),
            string.concat("x", _symbol),
            _underlyingAsset,
            poolAddress,
            address(reservesManager)
        );

        debtToken = new DebtToken(
            string.concat("debt", _name),
            string.concat("debt", _symbol),
            _underlyingAsset,
            poolAddress,
            address(reservesManager)
        );

        reservesManager.initReserve(
            _underlyingAsset,
            _baseVariableBorrowRate,
            _interestRateSlope,
            address(xtoken),
            address(debtToken)
        );

        underlyingAssetToXtoken[_underlyingAsset] = address(xtoken);
        underlyingAssetToDebtToken[_underlyingAsset] = address(debtToken);
        isAvailable[_underlyingAsset] = true;

        priceOracle = new PriceOracleMock(_priceFeedAddress, _decimals);

        underlyingAssetToPriceOracle[_underlyingAsset] = address(priceOracle);
        tokens.push(_underlyingAsset);

        return (address(xtoken), address(debtToken), address(priceOracle));
    }

    function getXToken() public view returns (XToken) {
        return xtoken;
    }

    function getDebtToken() public view returns (DebtToken) {
        return debtToken;
    }

    function getPriceOracle() public view returns (PriceOracle) {
        return priceOracle;
    }
}
