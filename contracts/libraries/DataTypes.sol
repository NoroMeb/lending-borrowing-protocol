// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

/**
 * @author  . MEBARKIA Abdenour
 * @title   . DataTypes
 * @dev     . Library containing a Reserve struct wich defines reserve properties .
 */

library DataTypes {
    struct Reserve {
        uint256 totalDeposited;
        uint256 totalBorrowed;
        uint256 utilizationRate;
        uint256 variableBorrowRate;
        uint256 baseVariableBorrowRate;
        uint256 interestRateSlope;
        uint256 variableBorrowIndex;
        uint256 liquidityRate;
        uint256 supplyIndex;
        uint256 lastUpdateTime;
        address xToken;
        address debtToken;
    }
}
