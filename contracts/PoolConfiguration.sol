// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "./tokenization/XToken.sol";
import "./tokenization/DebtToken.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./PriceOracle.sol";

import {DataTypes} from "./libraries/DataTypes.sol";

contract PoolConfiguration is Ownable {
    address public poolAddress;
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
            poolAddress
        );

        debtToken = new DebtToken(
            string.concat("debt", _name),
            string.concat("debt", _symbol),
            _underlyingAsset,
            poolAddress
        );

        initReserve(
            _underlyingAsset,
            _interestRateSlope,
            _baseVariableBorrowRate
        );

        underlyingAssetToXtoken[_underlyingAsset] = address(xtoken);
        underlyingAssetToDebtToken[_underlyingAsset] = address(debtToken);
        isAvailable[_underlyingAsset] = true;

        priceOracle = new PriceOracle(_priceFeedAddress, _decimals);

        underlyingAssetToPriceOracle[_underlyingAsset] = address(priceOracle);

        return (address(xtoken), address(debtToken), address(priceOracle));
    }

    function initReserve(
        address _underlyingAsset,
        uint256 _baseVariableBorrowRate,
        uint256 _interestRateSlope
    ) internal {
        uint256 totalDeposited = 0;
        uint256 totalBorrowed = 0;
        uint256 initialUitilizationRate = 0;
        uint256 initialVariableBorrowIndex = 1000000000000000000;
        uint256 lastUpdateTime = block.timestamp;
        uint256 initialVariableBorrowRate = 0;

        // DataTypes.Reserve storage reserve;

        DataTypes.Reserve memory reserve = DataTypes.Reserve(
            totalDeposited,
            totalBorrowed,
            initialUitilizationRate,
            initialVariableBorrowRate,
            _baseVariableBorrowRate,
            _interestRateSlope,
            initialVariableBorrowIndex,
            lastUpdateTime
        );
        underlyingAssetToReserve[_underlyingAsset] = reserve;
    }

    function getUnderlyingAssetToReserve(address _underlyingAsset)
        public
        view
        returns (DataTypes.Reserve memory)
    {
        return underlyingAssetToReserve[_underlyingAsset];
    }

    function setUnderlyingAssetToReserve(
        address _underlyingAsset,
        DataTypes.Reserve memory reserve
    ) public {
        underlyingAssetToReserve[_underlyingAsset] = reserve;
    }
}
