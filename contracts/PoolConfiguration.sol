// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "./tokenization/XToken.sol";
import "./tokenization/DebtToken.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./PriceOracle.sol";

import "./ReservesManager.sol";

import {DataTypes} from "./libraries/DataTypes.sol";

/**
 * @author  . MEBARKIA Abdenour
 * @title   . PoolConfiguration
 * @dev     . To add new token and all the related configuration
 */

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

    address[] public tokens;

    constructor(address _poolAddress) {
        poolAddress = _poolAddress;
    }

    function setReserveManagerContract(address _reserveManagerAddress)
        external
        onlyOwner
    {
        reservesManager = ReservesManager(_reserveManagerAddress);
    }

    /**
     * @dev     . Add new token to the protocol utilisation panel
     * @param   _name  . the name of the underlying asset to be added
     * @param   _symbol  .  the symbol of the underlying asset to be added
     * @param   _underlyingAsset  .  the address of the underlying asset to be added
     * @param   _priceFeedAddress  . the address of the underlying asset's price feed contract
     * @param   _decimals  .  the name of the underlying asset to be added
     * @param   _baseVariableBorrowRate  . base variable borrow rate to calculate the interests/debts
     * @param   _interestRateSlope  . interest rate slope to calculate the interests/debts
     * @return  address  . the xToken address of the underlying asset
     * @return  address  . the dentToken address of the underlying asset
     * @return  address  . the priceOracle address
     */
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
        virtual
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

        priceOracle = new PriceOracle(_priceFeedAddress);

        underlyingAssetToPriceOracle[_underlyingAsset] = address(priceOracle);
        tokens.push(_underlyingAsset);

        return (address(xtoken), address(debtToken), address(priceOracle));
    }

    function getTokens() public view returns (address[] memory) {
        return tokens;
    }
}
