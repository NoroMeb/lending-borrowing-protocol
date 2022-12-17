// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract PriceOracle {
    AggregatorV3Interface public priceFeed;
    uint256 public decimals;

    constructor(address _priceFeedAddress, uint256 _decimals) {
        priceFeed = AggregatorV3Interface(_priceFeedAddress);
        decimals = _decimals;
    }

    function getLatestPrice() public view returns (uint256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        if (decimals == 8) {
            uint256 latestPrice = uint256(price / 1e8);
            return latestPrice;
        }
        if (decimals == 18) {
            uint256 latestPrice = uint256(price / 1e18);
            return latestPrice;
        }
    }
}
