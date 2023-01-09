// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "./../PriceOracle.sol";

/**
 * @author  . Mebarkia Abdenour
 * @title   . PriceOracle
 * @dev     . get a price of specified pair - e.g (dai / usd )
 */

contract PriceOracleMock is PriceOracle {
    uint256 public decimals;

    constructor(address _priceFeedAddress, uint256 _decimals)
        PriceOracle(_priceFeedAddress)
    {
        priceFeed = AggregatorV3Interface(_priceFeedAddress);
        decimals = _decimals;
    }

    /**
     * @dev     .  get the latest price of an asset
     * @return  uint256  . the latest price of an asset
     */
    function getLatestPrice() public view override returns (uint256) {
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
