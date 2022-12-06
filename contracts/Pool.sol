// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./PoolConfiguration.sol";
import "../interfaces/IXToken.sol";

contract Pool is Ownable {
    PoolConfiguration public poolConfiguration;

    function setPoolConfigurationAddress(address _poolConfigurationAddress)
        external
        onlyOwner
    {
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

    function borrow(address _asset, uint256 _amount) public {
        require(_amount > 0, "insufficient amount");
        require(
            poolConfiguration.getIsAvailable(_asset),
            "Token not available"
        );

        uint256 userBalance = IXToken(xtoken).balanceOf(msg.sender);
    }

    function withdraw(address _asset, uint256 _amount) public {
        require(_amount > 0, "Amount must be greater than 0");
        require(
            poolConfiguration.getIsAvailable(_asset),
            "Token not available"
        );

        address xtoken = poolConfiguration.getXToken(_asset);
        uint256 userBalance = IXToken(xtoken).balanceOf(msg.sender);
        require(userBalance > 0, "Don't have any funds");

        IXToken(xtoken).transferUnderlyingAssetTo(msg.sender, _amount);
        IXToken(xtoken).burn(msg.sender, _amount);
    }

    function repay() public {}
}
