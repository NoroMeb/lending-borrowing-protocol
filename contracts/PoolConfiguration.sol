// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "./tokenization/XToken.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

import "./PriceOracle.sol";

contract PoolConfiguration is Ownable {
    address public poolAddress;
    XToken internal xtoken;
    PriceOracle internal priceOracle;

    mapping(address => address) public underlyingAssetToXtoken;
    mapping(address => bool) public isAvailable;
    mapping(address => address) public underlyingAssetToPriceOracle;

    constructor(address _poolAddress) public {
        poolAddress = _poolAddress;
    }

    function addToken(
        string memory _name,
        string memory _symbol,
        address _underlyingAsset,
        address _priceFeedAddress,
        uint256 _decimals
    ) external onlyOwner returns (address, address) {
        xtoken = new XToken(_name, _symbol, _underlyingAsset, poolAddress);

        underlyingAssetToXtoken[_underlyingAsset] = address(xtoken);
        isAvailable[_underlyingAsset] = true;

        priceOracle = new PriceOracle(_priceFeedAddress, _decimals);

        underlyingAssetToPriceOracle[_underlyingAsset] = address(priceOracle);

        return (address(xtoken), address(priceOracle));
    }
}
