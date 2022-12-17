// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../interfaces/IXToken.sol";
import "./PoolConfiguration.sol";
import "@ds-math/src/math.sol";

contract ReservesManager is DSMath {
    PoolConfiguration public poolConfiguration;

    uint256 public immutable interestRateSlope;
    uint256 public immutable baseVariableBorrowRate;

    constructor(
        address _poolConfigurationAddress,
        uint256 _interestRateSlope,
        uint256 _baseVariableBorrowRate
    ) public {
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
        returns (uint256)
    {
        uint256 utilizationRate;
        address xtoken = poolConfiguration.underlyingAssetToXtoken(
            _underlyingAsset
        );
        uint256 totalBorrowed = IXToken(xtoken).getTotalBorrowed();
        uint256 totalDeposited = IXToken(xtoken).getTotalDeposited();

        if (totalDeposited == 0) {
            utilizationRate = 0;
        } else {
            utilizationRate = wdiv(totalBorrowed, totalDeposited) * 100;
        }

        return utilizationRate;
    }

    function updateVariableBorrowRate(address _underlyingAsset)
        public
        returns (uint256)
    {
        uint256 utilizationRate = updateUtilizationRate(_underlyingAsset);

        uint256 variableBorrowRate = add(
            baseVariableBorrowRate,
            (wmul(wdiv(utilizationRate, 100 * 10**18), interestRateSlope))
        );

        return variableBorrowRate;
    }
}
