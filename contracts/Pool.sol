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
    mapping(address => mapping(address => uint256))
        internal userToAssetToDebtAmount;

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
        require(poolConfiguration.isAvailable(_asset), "token not available");
        address xtoken = poolConfiguration.underlyingAssetToXtoken(_asset);
        IERC20(_asset).transferFrom(msg.sender, xtoken, _amount);
        IXToken(xtoken).mint(msg.sender, _amount);

        uint256 totalDeposited = IXToken(xtoken).getTotalDeposited();
        totalDeposited = totalDeposited + _amount;
        IXToken(xtoken).setTotalDeposited(totalDeposited);
    }

    function borrow(address _asset, uint256 _amount) public returns (uint256) {
        address xtoken = poolConfiguration.underlyingAssetToXtoken(_asset);

        bool isValid = poolLogic.validateBorrow(msg.sender, _asset, _amount);

        if (!isValid) {
            return 0;
        } else {
            IXToken(xtoken).transferUnderlyingAssetTo(msg.sender, _amount);
            IXToken(xtoken).burn(msg.sender, _amount);
            userToAssetToDebtAmount[msg.sender][_asset] =
                userToAssetToDebtAmount[msg.sender][_asset] +
                _amount;
            uint256 totalBorrowed = IXToken(xtoken).getTotalBorrowed();
            totalBorrowed = totalBorrowed + _amount;
            IXToken(xtoken).setTotalBorrowed(totalBorrowed);
            return _amount;
        }
    }

    function withdraw(address _asset, uint256 _amount)
        public
        returns (uint256)
    {
        address xtoken = poolConfiguration.underlyingAssetToXtoken(_asset);

        bool isValid = poolLogic.validateWithdraw(msg.sender, _asset, _amount);

        if (!isValid) {
            return 0;
        } else {
            IXToken(xtoken).transferUnderlyingAssetTo(msg.sender, _amount);
            IXToken(xtoken).burn(msg.sender, _amount);
            uint256 totalDeposited = IXToken(xtoken).getTotalDeposited();
            totalDeposited = totalDeposited - _amount;
            IXToken(xtoken).setTotalDeposited(totalDeposited);

            return _amount;
        }
    }

    function repay(address _asset, uint256 _amount) public {
        require(_amount > 0, "insufficient amount");
        require(poolConfiguration.isAvailable(_asset), "token not available");
        require(
            userToAssetToDebtAmount[msg.sender][_asset] > 0,
            "doesnt have a debt to pay"
        );
        require(
            _amount <= userToAssetToDebtAmount[msg.sender][_asset],
            "the amount exceeds the debt"
        );

        address xtoken = poolConfiguration.underlyingAssetToXtoken(_asset);
        IERC20(_asset).transferFrom(msg.sender, xtoken, _amount);
        IXToken(xtoken).mint(msg.sender, _amount);

        userToAssetToDebtAmount[msg.sender][_asset] =
            userToAssetToDebtAmount[msg.sender][_asset] -
            _amount;
    }
}
