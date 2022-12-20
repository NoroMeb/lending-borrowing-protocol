// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../interfaces/IXToken.sol";
import "../interfaces/IDebtToken.sol";
import "./PoolConfiguration.sol";
import "@ds-math/src/math.sol";

contract ReservesManager is DSMath {
    PoolConfiguration public poolConfiguration;

    uint256 public immutable interestRateSlope;
    uint256 public immutable baseVariableBorrowRate;

    uint256 lastUpdateTime;
    uint256 public constant SECONDS_PER_YEAR = 365 days;
    uint256 internal variableBorrowIndex = 1;

    constructor(
        address _poolConfigurationAddress,
        uint256 _interestRateSlope,
        uint256 _baseVariableBorrowRate
    ) {
        poolConfiguration = PoolConfiguration(_poolConfigurationAddress);
        interestRateSlope = _interestRateSlope;
        baseVariableBorrowRate = _baseVariableBorrowRate;
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

    function updateUtilizationRate(address _underlyingAsset)
        public
        view
        returns (uint256)
    {
        uint256 utilizationRate;
        address xtoken = poolConfiguration.underlyingAssetToXtoken(
            _underlyingAsset
        );
        address debtToken = poolConfiguration.underlyingAssetToDebtToken(
            _underlyingAsset
        );
        uint256 totalDeposited = IXToken(xtoken).getTotalDeposited();
        uint256 totalBorrowed = IDebtToken(debtToken).getTotalBorrowed();

        if (totalDeposited == 0) {
            utilizationRate = 0;
        } else {
            utilizationRate = wdiv(totalBorrowed, totalDeposited) * 100;
        }

        return utilizationRate;
    }

    function updateVariableBorrowRate(address _underlyingAsset)
        public
        view
        returns (uint256)
    {
        uint256 utilizationRate = updateUtilizationRate(_underlyingAsset);

        uint256 variableBorrowRate = add(
            baseVariableBorrowRate,
            (wmul(wdiv(utilizationRate, 100 * 10**18), interestRateSlope))
        );

        return variableBorrowRate;
    }

    function updateState(address _underlyingAsset) public returns (uint256) {
        uint256 secondsSinceLastupdate = block.timestamp - lastUpdateTime;
        uint256 variableBorrowRate = updateVariableBorrowRate(_underlyingAsset);
        uint256 variableBorrowRatePerSecond = variableBorrowRate /
            SECONDS_PER_YEAR;

        lastUpdateTime = block.timestamp;
        return variableBorrowRatePerSecond;
    }

    function updateVariableBorrowIndex(
        uint256 _variableBorrowRatePerSecond,
        uint256 _secondsSinceLastupdate
    ) public returns (uint256) {
        // variableBorrowIndex = wmul(
        //     variableBorrowIndex,
        //     add(1, wmul(_variableBorrowRatePerSecond, _secondsSinceLastupdate))
        // );

        variableBorrowIndex =
            variableBorrowIndex *
            (1 + _variableBorrowRatePerSecond * _secondsSinceLastupdate);

        return variableBorrowIndex;
    }
}
