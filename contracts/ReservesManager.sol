// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

import "./PoolConfiguration.sol";

contract ReservesManager {
    PoolConfiguration public poolConfiguration;
    uint256 public amountBorrowed;

    constructor(address _poolConfigurationAddress) public {
        poolConfiguration = PoolConfiguration(_poolConfigurationAddress);
    }

    function getReserveBalance(address _underlyingAsset)
        public
        view
        returns (uint256)
    {
        require(
            poolConfiguration.getIsAvailable(_underlyingAsset),
            "Token not available"
        );
        address reserve = poolConfiguration.getXToken(_underlyingAsset);
        uint256 reserveBalance = IERC20(_underlyingAsset).balanceOf(reserve);
    }
}
