// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "./tokenization/XToken.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract PoolConfiguration is Ownable {
    XToken public xtoken;
    address public poolAddress;

    mapping(address => address) public underlyingAssetToXtoken;
    mapping(address => bool) public IsAvailable;

    constructor(address _poolAddress) public {
        poolAddress = _poolAddress;
    }

    function addToken(
        address _underlyingAsset,
        string memory _name,
        string memory _symbol
    ) public onlyOwner {
        xtoken = new XToken(_name, _symbol, _underlyingAsset, poolAddress);
        underlyingAssetToXtoken[_underlyingAsset] = address(xtoken);
        IsAvailable[_underlyingAsset] = true;
    }

    function getXToken(address _underlyingAsset) public view returns (address) {
        return underlyingAssetToXtoken[_underlyingAsset];
    }

    function getIsAvailable(address _underlyingAsset)
        public
        view
        returns (bool)
    {
        return IsAvailable[_underlyingAsset];
    }
}
