// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../interfaces/IXToken.sol";
import "../interfaces/IDebtToken.sol";
import "./PoolConfiguration.sol";
import "@ds-math/src/math.sol";

import {DataTypes} from "./libraries/DataTypes.sol";

/**
 * @author  . MEBARKIA Abdenour
 * @title   . ReservesManager
 * @dev     . Manage reserves and calculates debt & interests indexes
 */

contract ReservesManager is DSMath {
    address public poolConfigurationAddress;
    address public poolAddress;

    uint256 public constant SECONDS_PER_YEAR = 365 days;

    mapping(address => DataTypes.Reserve) public underlyingAssetToReserve;

    modifier onlyPool() {
        require(msg.sender == poolAddress, "caller must be pool");
        _;
    }

    modifier onlyPoolConfiguration() {
        require(
            msg.sender == poolConfigurationAddress,
            "caller must be pool configuration"
        );
        _;
    }

    constructor(address _poolConfigurationAddress, address _poolAddress) {
        poolConfigurationAddress = _poolConfigurationAddress;
        poolAddress = _poolAddress;
    }

    function getReserve(address _underlyingAsset)
        public
        view
        returns (DataTypes.Reserve memory)
    {
        return underlyingAssetToReserve[_underlyingAsset];
    }

    /**
     * @dev     . calculates the utilization rate of a reserve based on the total deposited / borrowed on the reserve
     * @param   _totalDeposited  . total amount deposited in a reserve
     * @param   _totalBorrowed  . total amount borrowed in a reserve
     * @return  uint256  . the utilization rate value
     */
    function updateUtilizationRate(
        uint256 _totalDeposited,
        uint256 _totalBorrowed
    ) internal pure returns (uint256) {
        uint256 utilizationRate;

        if (_totalDeposited == 0) {
            utilizationRate = 0;
        } else {
            utilizationRate = wdiv(_totalBorrowed, _totalDeposited);
        }

        return utilizationRate;
    }

    /**
     * @dev     . calculates the variable borrow rate of a reserve based on utilization rate, base variable borrow rate
     * & intereste rate slope of a reserve
     * @param   _utilizationRate  .  utilization rate of a reserve
     * @param   _baseVariableBorrowRate  . base variable borrow rate of a reserve
     * @param   _interestRateSlope  . intereste rate slope of a reserve
     * @return  uint256  . the variable borrow value
     */
    function updateVariableBorrowRate(
        uint256 _utilizationRate,
        uint256 _baseVariableBorrowRate,
        uint256 _interestRateSlope
    ) internal pure returns (uint256) {
        uint256 variableBorrowRate = add(
            _baseVariableBorrowRate,
            (wmul(_utilizationRate, _interestRateSlope))
        );

        return variableBorrowRate;
    }

    /**
     * @dev     . calculates the index of debt or interest of all users
     * @param   _latestIndex  . latest index
     * @param   _rate  . variable borrow rate / liquidity rate , dependes of the index we want to calculate
     * @param   _secondsSinceLastupdate  . number of seconds since latest update of a reserve
     * @return  uint256  . the index value
     */
    function updateIndex(
        uint256 _latestIndex,
        uint256 _rate,
        uint256 _secondsSinceLastupdate
    ) internal pure returns (uint256) {
        uint256 ratePerSecond = _rate / SECONDS_PER_YEAR;

        uint256 index = wmul(
            _latestIndex,
            add(1000000000000000000, ratePerSecond * _secondsSinceLastupdate)
        );

        return index;
    }

    /**
     * @dev     . update all the variable properties of a reserve, this function is called
     * whenever a user call this functions : supply, borrow, withdraw, repay
     * @param   _underlyingAsset  . The address of the underlying asset of the reserve
     * @param   _amount  . the amount user passed on one of the function quoted above
     * @param   _operation  . an integer that represents which function the user called
     *                           operation : value
     *                           supply : 0
     *                           borrow : 1
     *                           withdraw : 2
     *                           repay : 3
     */
    function updateState(
        address _underlyingAsset,
        uint256 _amount,
        uint256 _operation
    ) public onlyPool {
        DataTypes.Reserve memory reserve;
        reserve = underlyingAssetToReserve[_underlyingAsset];

        uint256 secondsSinceLastupdate = block.timestamp -
            reserve.lastUpdateTime;

        if (_operation == 0) {
            reserve.totalDeposited = reserve.totalDeposited + _amount;
        }
        if (_operation == 1) {
            reserve.totalBorrowed = reserve.totalBorrowed + _amount;
        }
        if (_operation == 2) {
            reserve.totalDeposited = reserve.totalDeposited - _amount;
        }
        if (_operation == 3) {
            reserve.totalBorrowed = reserve.totalBorrowed - _amount;
        }

        uint256 utilizationRate = updateUtilizationRate(
            reserve.totalDeposited,
            reserve.totalBorrowed
        );
        uint256 variableBorrowRate = updateVariableBorrowRate(
            utilizationRate,
            reserve.baseVariableBorrowRate,
            reserve.interestRateSlope
        );

        uint256 liquidityRate = wmul(variableBorrowRate, utilizationRate);

        uint256 variableBorrowIndex = updateIndex(
            reserve.variableBorrowIndex,
            variableBorrowRate,
            secondsSinceLastupdate
        );

        uint256 supplyIndex = updateIndex(
            reserve.supplyIndex,
            liquidityRate,
            secondsSinceLastupdate
        );

        reserve.utilizationRate = utilizationRate;
        reserve.variableBorrowRate = variableBorrowRate;
        reserve.variableBorrowIndex = variableBorrowIndex;
        reserve.liquidityRate = liquidityRate;
        reserve.supplyIndex = supplyIndex;
        reserve.lastUpdateTime = block.timestamp;

        underlyingAssetToReserve[_underlyingAsset] = reserve;
    }

    /**
     * @dev     . returns the variable borrow index needed to calculate the balance of user debtToken
     * @param   _underlyingAsset  . the adress of the underlying asset of the debtToken
     * @return  uint256  . variable borrow index
     */
    function getVariableBorrowIndexSinceLastUpdate(address _underlyingAsset)
        public
        view
        returns (uint256)
    {
        DataTypes.Reserve memory reserve;
        reserve = underlyingAssetToReserve[_underlyingAsset];

        uint256 secondsSinceLastupdate = block.timestamp -
            reserve.lastUpdateTime;

        uint256 variableBorrowIndex = updateIndex(
            reserve.variableBorrowIndex,
            reserve.variableBorrowRate,
            secondsSinceLastupdate
        );

        return variableBorrowIndex;
    }

    /**
     * @dev     . returns the supply index needed to calculate the balance of user xToken
     * @param   _underlyingAsset  . the adress of the underlying asset of the xToken
     * @return  uint256  . supply index
     */
    function getSupplyIndexSinceLastUpdate(address _underlyingAsset)
        public
        view
        returns (uint256)
    {
        DataTypes.Reserve memory reserve;
        reserve = underlyingAssetToReserve[_underlyingAsset];

        uint256 secondsSinceLastupdate = block.timestamp -
            reserve.lastUpdateTime;

        uint256 supplyIndex = updateIndex(
            reserve.supplyIndex,
            reserve.liquidityRate,
            secondsSinceLastupdate
        );

        return supplyIndex;
    }

    /**
     * @dev     . init a new reserve when adding new available token, this can only be called by PoolConfiguration
     * @param   _underlyingAsset  . the address of the underlying asset of the new reserve
     * @param   _baseVariableBorrowRate  . base variable borrow rate of the new reserve
     * @param   _interestRateSlope  . interest rate slope of the new reserve
     * @param   _xToken  . address of xToken of the new reserve
     * @param   _debtToken  . address of debtToken of the new reserve
     */
    function initReserve(
        address _underlyingAsset,
        uint256 _baseVariableBorrowRate,
        uint256 _interestRateSlope,
        address _xToken,
        address _debtToken
    ) public onlyPoolConfiguration {
        DataTypes.Reserve memory reserve;

        reserve = DataTypes.Reserve(
            0,
            0,
            0,
            0,
            _baseVariableBorrowRate,
            _interestRateSlope,
            1000000000000000000,
            0,
            1000000000000000000,
            block.timestamp,
            _xToken,
            _debtToken
        );
        underlyingAssetToReserve[_underlyingAsset] = reserve;
    }

    // Reseve getters

    function getTotalDeposited(address _underlyingAsset)
        public
        view
        returns (uint256)
    {
        return underlyingAssetToReserve[_underlyingAsset].totalDeposited;
    }

    function getTotalBorrowed(address _underlyingAsset)
        public
        view
        returns (uint256)
    {
        return underlyingAssetToReserve[_underlyingAsset].totalBorrowed;
    }

    function getUtilizationRate(address _underlyingAsset)
        public
        view
        returns (uint256)
    {
        return underlyingAssetToReserve[_underlyingAsset].utilizationRate;
    }

    function getVariableBorrowRate(address _underlyingAsset)
        public
        view
        returns (uint256)
    {
        return underlyingAssetToReserve[_underlyingAsset].variableBorrowRate;
    }

    function getBaseVariableBorrowRate(address _underlyingAsset)
        public
        view
        returns (uint256)
    {
        return
            underlyingAssetToReserve[_underlyingAsset].baseVariableBorrowRate;
    }

    function getInterestRateSlope(address _underlyingAsset)
        public
        view
        returns (uint256)
    {
        return underlyingAssetToReserve[_underlyingAsset].interestRateSlope;
    }

    function getVariableBorrowIndex(address _underlyingAsset)
        public
        view
        returns (uint256)
    {
        return underlyingAssetToReserve[_underlyingAsset].variableBorrowIndex;
    }

    function getLiquidityRate(address _underlyingAsset)
        public
        view
        returns (uint256)
    {
        return underlyingAssetToReserve[_underlyingAsset].liquidityRate;
    }

    function getSupplyIndex(address _underlyingAsset)
        public
        view
        returns (uint256)
    {
        return underlyingAssetToReserve[_underlyingAsset].supplyIndex;
    }

    function getLastUpdateTime(address _underlyingAsset)
        public
        view
        returns (uint256)
    {
        return underlyingAssetToReserve[_underlyingAsset].lastUpdateTime;
    }

    function getXToken(address _underlyingAsset) public view returns (address) {
        return underlyingAssetToReserve[_underlyingAsset].xToken;
    }

    function getDebtToken(address _underlyingAsset)
        public
        view
        returns (address)
    {
        return underlyingAssetToReserve[_underlyingAsset].debtToken;
    }
}
