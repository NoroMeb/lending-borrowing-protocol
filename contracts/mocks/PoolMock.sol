// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "./../Pool.sol";

contract PoolMock is Pool {
    function getUserToAssetToDebtAmount(address user, address asset)
        public
        view
        returns (uint256)
    {
        return userToAssetToDebtAmount[user][asset];
    }
}
