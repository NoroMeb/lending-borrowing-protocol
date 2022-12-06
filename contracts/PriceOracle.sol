// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract PriceOracle {
    AggregatorV3Interface internal priceFeed;

    function getLatestPrice(address _priceFeedAddress, uint256 _decimals)
        public
        returns (uint256)
    {
        priceFeed = AggregatorV3Interface(_priceFeedAddress);

        (, int256 price, , , ) = priceFeed.latestRoundData();
        if (_decimals == 8) {
            return uint256(price / 1e8);
        }
        if (_decimals == 18) {
            return uint256(price / 1e18);
        }
    }
}
