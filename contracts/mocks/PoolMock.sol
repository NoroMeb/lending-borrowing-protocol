// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "./../Pool.sol";

contract PoolMock is Pool {
    function getUserToAssetToAmountBorrowed(address user, address asset)
        public
        view
        returns (uint256)
    {
        return userToAssetToAmountBorrowed[user][asset];
    }
}
