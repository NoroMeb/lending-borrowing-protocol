// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "./tokenization/XToken.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

import "./PriceOracle.sol";

contract PoolConfiguration is Ownable {
    XToken public xtoken;
    address public poolAddress;
    PriceOracle public priceOracle;

    mapping(address => address) public underlyingAssetToXtoken;
    mapping(address => bool) public IsAvailable;
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
    ) public onlyOwner {
        xtoken = new XToken(_name, _symbol, _underlyingAsset, poolAddress);

        underlyingAssetToXtoken[_underlyingAsset] = address(xtoken);
        IsAvailable[_underlyingAsset] = true;

        priceOracle = new PriceOracle(_priceFeedAddress, _decimals);

        underlyingAssetToPriceOracle[_underlyingAsset] = address(priceOracle);
    }
}
