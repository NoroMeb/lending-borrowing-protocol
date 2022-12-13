// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../interfaces/IXToken.sol";
import "./PoolConfiguration.sol";

contract ReservesManager {
    PoolConfiguration public poolConfiguration;
    uint256 public amountBorrowed;
    uint256 public utilizationRatio;

    constructor(address _poolConfigurationAddress) public {
        poolConfiguration = PoolConfiguration(_poolConfigurationAddress);
    }

    function getReserveBalance(address _underlyingAsset)
        public
        view
        returns (uint256)
    {
        require(
            poolConfiguration.isAvailable(_underlyingAsset),
            "Token not available"
        );
        address reserve = poolConfiguration.underlyingAssetToXtoken(
            _underlyingAsset
        );
        uint256 reserveBalance = IERC20(_underlyingAsset).balanceOf(reserve);

        return reserveBalance;
    }

    function updateUtilizationRatio(address _underlyingAsset)
        public
        returns (uint256)
    {
        address xtoken = poolConfiguration.underlyingAssetToXtoken(
            _underlyingAsset
        );
        uint256 totalBorrowed = IXToken(xtoken).getTotalBorrowed();
        uint256 totalDeposited = IXToken(xtoken).getTotalDeposited();

        if (totalDeposited == 0) {
            utilizationRatio = 0;
        } else {
            utilizationRatio = totalBorrowed / totalDeposited;
        }

        return utilizationRatio;
    }
}
