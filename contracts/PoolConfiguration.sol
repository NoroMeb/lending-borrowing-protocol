// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "./tokenization/XToken.sol";
import "./tokenization/DebtToken.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./PriceOracle.sol";

import "./ReservesManager.sol";

import {DataTypes} from "./libraries/DataTypes.sol";

contract PoolConfiguration is Ownable {
    address public poolAddress;
    ReservesManager public reservesManager;
    XToken internal xtoken;
    DebtToken internal debtToken;
    PriceOracle internal priceOracle;

    mapping(address => address) public underlyingAssetToXtoken;
    mapping(address => address) public underlyingAssetToDebtToken;
    mapping(address => bool) public isAvailable;
    mapping(address => address) public underlyingAssetToPriceOracle;
    mapping(address => DataTypes.Reserve) public underlyingAssetToReserve;

    constructor(address _poolAddress) {
        poolAddress = _poolAddress;
    }

    function setReserveManagerContract(address _reserveManagerAddress)
        external
        onlyOwner
    {
        reservesManager = ReservesManager(_reserveManagerAddress);
    }

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

        priceOracle = new PriceOracle(_priceFeedAddress, _decimals);

        underlyingAssetToPriceOracle[_underlyingAsset] = address(priceOracle);

        return (address(xtoken), address(debtToken), address(priceOracle));
    }
}
