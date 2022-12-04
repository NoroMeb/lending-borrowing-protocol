// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "./PoolConfiguration.sol";
import "../interfaces/IXToken.sol";

contract Pool {
    PoolConfiguration poolConfiguration;

    constructor(address _poolConfigurationAddress) public {
        poolConfiguration = PoolConfiguration(_poolConfigurationAddress);
    }

    function supply(address _asset, uint256 _amount) public {
        require(_amount > 0, "insufficient amount");
        require(
            poolConfiguration.getIsAvailable(_asset),
            "Token not available"
        );
        address xtoken = poolConfiguration.getXToken(_asset);
        IERC20(_asset).transferFrom(msg.sender, xtoken, _amount);
        IXToken(xtoken).mint(msg.sender, _amount);
    }

    function borrow() public {}

    function withdraw() public {}

    function repay() public {}
}
