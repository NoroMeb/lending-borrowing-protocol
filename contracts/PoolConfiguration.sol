// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "./tokenization/XToken.sol";
import "./tokenization/DebtToken.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

import "./PriceOracle.sol";

contract PoolConfiguration is Ownable {
    address public poolAddress;
    XToken internal xtoken;
    DebtToken internal debtToken;
    PriceOracle internal priceOracle;

    mapping(address => address) public underlyingAssetToXtoken;
    mapping(address => address) public underlyingAssetToDebtToken;
    mapping(address => bool) public isAvailable;
    mapping(address => address) public underlyingAssetToPriceOracle;

    constructor(address _poolAddress) {
        poolAddress = _poolAddress;
    }

    function addToken(
        string memory _name,
        string memory _symbol,
        address _underlyingAsset,
        address _priceFeedAddress,
        uint256 _decimals
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

        underlyingAssetToXtoken[_underlyingAsset] = address(xtoken);
        underlyingAssetToDebtToken[_underlyingAsset] = address(debtToken);
        isAvailable[_underlyingAsset] = true;

        priceOracle = new PriceOracle(_priceFeedAddress, _decimals);

        underlyingAssetToPriceOracle[_underlyingAsset] = address(priceOracle);

        return (address(xtoken), address(debtToken), address(priceOracle));
    }
}
