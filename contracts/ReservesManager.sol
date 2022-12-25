// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../interfaces/IXToken.sol";
import "../interfaces/IDebtToken.sol";
import "./PoolConfiguration.sol";
import "@ds-math/src/math.sol";

import {DataTypes} from "./libraries/DataTypes.sol";

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

    function updateUtilizationRate(
        uint256 _totalDeposited,
        uint256 _totalBorrowed
    ) public pure returns (uint256) {
        uint256 utilizationRate;

        if (_totalDeposited == 0) {
            utilizationRate = 0;
        } else {
            utilizationRate = wdiv(_totalBorrowed, _totalDeposited);
        }

        return utilizationRate;
    }

    function updateVariableBorrowRate(
        uint256 _utilizationRate,
        uint256 _baseVariableBorrowRate,
        uint256 _interestRateSlope
    ) public pure returns (uint256) {
        uint256 variableBorrowRate = add(
            _baseVariableBorrowRate,
            (wmul(_utilizationRate, _interestRateSlope))
        );

        return variableBorrowRate;
    }

    function updateVariableBorrowIndex(
        uint256 _latestVariableBorrowIndex,
        uint256 _variableBorrowRate,
        uint256 _secondsSinceLastupdate
    ) public pure returns (uint256) {
        uint256 variableBorrowRatePerSecond = _variableBorrowRate /
            SECONDS_PER_YEAR;

        uint256 variableBorrowIndex = wmul(
            _latestVariableBorrowIndex,
            add(
                1000000000000000000,
                variableBorrowRatePerSecond * _secondsSinceLastupdate
            )
        );

        return variableBorrowIndex;
    }

    // operation : value
    // supply : 0
    // borrow : 1
    // withdraw : 2
    // repay : 3

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
        uint256 variableBorrowIndex = updateVariableBorrowIndex(
            reserve.variableBorrowIndex,
            variableBorrowRate,
            secondsSinceLastupdate
        );

        reserve.utilizationRate = utilizationRate;
        reserve.variableBorrowRate = variableBorrowRate;
        reserve.variableBorrowIndex = variableBorrowIndex;

        reserve.lastUpdateTime = block.timestamp;

        underlyingAssetToReserve[_underlyingAsset] = reserve;
    }

    function initReserve(
        address _underlyingAsset,
        uint256 _baseVariableBorrowRate,
        uint256 _interestRateSlope,
        address _xToken,
        address _debtToken
    ) public onlyPoolConfiguration {
        uint256 totalDeposited = 0;
        uint256 totalBorrowed = 0;
        uint256 initialUitilizationRate = 0;
        uint256 initialVariableBorrowIndex = 1000000000000000000;
        uint256 lastUpdateTime = block.timestamp;
        uint256 initialVariableBorrowRate = 0;

        DataTypes.Reserve memory reserve;

        reserve = DataTypes.Reserve(
            totalDeposited,
            totalBorrowed,
            initialUitilizationRate,
            initialVariableBorrowRate,
            _baseVariableBorrowRate,
            _interestRateSlope,
            initialVariableBorrowIndex,
            lastUpdateTime,
            _xToken,
            _debtToken
        );
        underlyingAssetToReserve[_underlyingAsset] = reserve;
    }

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
