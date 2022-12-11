// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "./PoolLogic.sol";
import "./PoolConfiguration.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IXToken.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract Pool is Ownable {
    PoolConfiguration public poolConfiguration;
    PoolLogic public poolLogic;

    function setPoolConfigurationAddress(address _poolConfigurationAddress)
        external
        onlyOwner
    {
        poolConfiguration = PoolConfiguration(_poolConfigurationAddress);
    }

    function setPoolLogicAddress(address _poolLogicAddress) external onlyOwner {
        poolLogic = PoolLogic(_poolLogicAddress);
    }

    function supply(address _asset, uint256 _amount) public {
        require(_amount > 0, "insufficient amount");
        require(poolConfiguration.isAvailable(_asset), "Token not available");
        address xtoken = poolConfiguration.underlyingAssetToXtoken(_asset);
        IERC20(_asset).transferFrom(msg.sender, xtoken, _amount);
        IXToken(xtoken).mint(msg.sender, _amount);
    }

    function borrow(address _asset, uint256 _amount) public returns (uint256) {
        address xtoken = poolConfiguration.underlyingAssetToXtoken(_asset);

        bool isValid = poolLogic.validateBorrow(msg.sender, _asset, _amount);

        if (!isValid) {
            return 0;
        } else {
            IXToken(xtoken).transferUnderlyingAssetTo(msg.sender, _amount);
            IXToken(xtoken).burn(msg.sender, _amount);

            return _amount;
        }
    }

    function withdraw(address _asset, uint256 _amount) public {
        require(_amount > 0, "Amount must be greater than 0");
        require(poolConfiguration.isAvailable(_asset), "Token not available");

        address xtoken = poolConfiguration.underlyingAssetToXtoken(_asset);
        uint256 userBalance = IXToken(xtoken).balanceOf(msg.sender);
        require(userBalance > 0, "Don't have any funds here");

        IXToken(xtoken).transferUnderlyingAssetTo(msg.sender, _amount);
        IXToken(xtoken).burn(msg.sender, _amount);
    }

    function repay() public {}
}
