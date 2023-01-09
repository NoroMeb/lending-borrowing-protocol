// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

/**
 * @author  . Mebarkia Abdenour
 * @title   . PriceOracle
 * @dev     . get a price of specified pair - e.g (dai / usd )
 */

contract PriceOracle {
    AggregatorV3Interface public priceFeed;

    constructor(address _priceFeedAddress) {
        priceFeed = AggregatorV3Interface(_priceFeedAddress);
    }

    /**
     * @dev     .  get the latest price of an asset
     * @return  uint256  . the latest price of an asset
     */
    function getLatestPrice() public view virtual returns (uint256) {
        (
            ,
            /*uint80 roundID*/
            int256 price, /*uint startedAt*/ /*uint timeStamp*/ /*uint80 answeredInRound*/
            ,
            ,

        ) = priceFeed.latestRoundData();
        return uint256(price);
    }
}
