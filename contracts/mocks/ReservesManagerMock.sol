// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "./../ReservesManager.sol";

contract ReservesManagerMock is ReservesManager {
    constructor(address _poolConfigurationAddress, address _poolAddress)
        ReservesManager(_poolConfigurationAddress, _poolAddress)
    {}

    function _updateUtilizationRate(
        uint256 _totalDeposited,
        uint256 _totalBorrowed
    ) public pure returns (uint256) {
        return super.updateUtilizationRate(_totalDeposited, _totalBorrowed);
    }

    function _updateVariableBorrowRate(
        uint256 _utilizationRate,
        uint256 _baseVariableBorrowRate,
        uint256 _interestRateSlope
    ) public pure returns (uint256) {
        return
            super.updateVariableBorrowRate(
                _utilizationRate,
                _baseVariableBorrowRate,
                _interestRateSlope
            );
    }

    function _updateIndex(
        uint256 _latestIndex,
        uint256 _rate,
        uint256 _secondsSinceLastupdate
    ) public pure returns (uint256) {
        return super.updateIndex(_latestIndex, _rate, _secondsSinceLastupdate);
    }
}
