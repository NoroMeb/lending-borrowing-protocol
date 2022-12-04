// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "./tokenization/XToken.sol";

contract PoolConfiguration {
    XToken public xtoken;

    mapping(address => address) public underlyingAssetToXtoken;
    mapping(address => bool) public IsAvailable;

    function addToken(
        address _underlyingAsset,
        string memory _name,
        string memory _symbol
    ) public {
        xtoken = new XToken(_name, _symbol);
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
