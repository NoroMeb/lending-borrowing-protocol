// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../interfaces/IXToken.sol";
import "../interfaces/IDebtToken.sol";
import "./PoolConfiguration.sol";
import "@ds-math/src/math.sol";

import {DataTypes} from "./libraries/DataTypes.sol";

contract ReservesManager is DSMath {
    PoolConfiguration public poolConfiguration;
    address public poolAddress;

    uint256 public constant SECONDS_PER_YEAR = 365 days;

    modifier onlyPool() {
        require(msg.sender == poolAddress, "caller must be pool");
        _;
    }

    constructor(address _poolConfigurationAddress, address _poolAddress) {
        poolConfiguration = PoolConfiguration(_poolConfigurationAddress);
        poolAddress = _poolAddress;
    }

    function getReserveBalance(address _underlyingAsset)
        public
        view
        returns (uint256)
    {
        require(
            poolConfiguration.isAvailable(_underlyingAsset),
            "token not available"
        );
        address reserve = poolConfiguration.underlyingAssetToXtoken(
            _underlyingAsset
        );
        uint256 reserveBalance = IERC20(_underlyingAsset).balanceOf(reserve);

        return reserveBalance;
    }

    function updateUtilizationRate(DataTypes.Reserve memory _reserve)
        public
        view
        returns (uint256)
    {
        uint256 totalDeposited = _reserve.totalDeposited;
        uint256 totalBorrowed = _reserve.totalBorrowed;

        if (totalDeposited == 0) {
            _reserve.utilizationRate = 0;
        } else {
            _reserve.utilizationRate = wdiv(totalBorrowed, totalDeposited);
        }

        return _reserve.utilizationRate;
    }

    function updateVariableBorrowRate(DataTypes.Reserve memory _reserve)
        public
        view
        returns (uint256)
    {
        _reserve.utilizationRate = updateUtilizationRate(_reserve);

        _reserve.variableBorrowRate = add(
            _reserve.baseVariableBorrowRate,
            (wmul(_reserve.utilizationRate, _reserve.interestRateSlope))
        );

        return _reserve.variableBorrowRate;
    }

    function updateVariableBorrowIndex(
        DataTypes.Reserve memory _reserve,
        uint256 _variableBorrowRatePerSecond,
        uint256 _secondsSinceLastupdate
    ) public pure returns (uint256) {
        _reserve.variableBorrowIndex = wmul(
            _reserve.variableBorrowIndex,
            add(
                1000000000000000000,
                _variableBorrowRatePerSecond * _secondsSinceLastupdate
            )
        );

        return _reserve.variableBorrowIndex;
    }

    function updateState(address _underlyingAsset)
        public
        view
        returns (uint256)
    {
        DataTypes.Reserve memory reserve = poolConfiguration
            .getUnderlyingAssetToReserve(_underlyingAsset);

        uint256 secondsSinceLastupdate = block.timestamp -
            reserve.lastUpdateTime;
        uint256 variableBorrowRate = updateVariableBorrowRate(reserve);
        uint256 variableBorrowRatePerSecond = variableBorrowRate /
            SECONDS_PER_YEAR;

        reserve.variableBorrowIndex = updateVariableBorrowIndex(
            reserve,
            variableBorrowRatePerSecond,
            secondsSinceLastupdate
        );

        reserve.lastUpdateTime = block.timestamp;
        return reserve.variableBorrowIndex;
    }
}
