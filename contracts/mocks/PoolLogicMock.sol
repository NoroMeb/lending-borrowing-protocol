// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "./../PoolLogic.sol";

contract PoolLogicMock is PoolLogic {
    constructor(address _poolConfigurationAddress)
        public
        PoolLogic(_poolConfigurationAddress)
    {}

    function _getUserBalanceInUSD(address _account, address _underlyingAsset)
        public
        returns (uint256)
    {
        return getUserBalanceInUSD(_account, _underlyingAsset);
    }

    function _getAmountInUSD(uint256 _amount, address _underlyingAsset)
        public
        returns (uint256)
    {
        return getAmountInUSD(_amount, _underlyingAsset);
    }
}
