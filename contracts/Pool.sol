// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "./PoolLogic.sol";
import "./PoolConfiguration.sol";
import "./ReservesManager.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IXToken.sol";
import "../interfaces/IDebtToken.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract Pool is Ownable {
    PoolConfiguration public poolConfiguration;
    PoolLogic public poolLogic;
    ReservesManager public reservesManager;

    mapping(address => mapping(address => address))
        public userToBorrowedAssetToCollateral;

    mapping(address => mapping(address => uint256))
        public userToCollateralToAmount;

    function setPoolConfigurationAddress(address _poolConfigurationAddress)
        external
        onlyOwner
    {
        poolConfiguration = PoolConfiguration(_poolConfigurationAddress);
    }

    function setPoolLogicAddress(address _poolLogicAddress) external onlyOwner {
        poolLogic = PoolLogic(_poolLogicAddress);
    }

    function setReservesManagerAddress(address _reservesManagerAddress)
        external
        onlyOwner
    {
        reservesManager = ReservesManager(_reservesManagerAddress);
    }

    function supply(address _asset, uint256 _amount) public {
        require(_amount > 0, "insufficient amount");
        require(poolConfiguration.isAvailable(_asset), "token not available");
        address xtoken = poolConfiguration.underlyingAssetToXtoken(_asset);
        IERC20(_asset).transferFrom(msg.sender, xtoken, _amount);
        IXToken(xtoken).mint(msg.sender, _amount);
        reservesManager.updateState(_asset, _amount, 0);
        userToCollateralToAmount[msg.sender][_asset] =
            userToCollateralToAmount[msg.sender][_asset] +
            _amount;
    }

    function borrow(
        address _asset,
        uint256 _amount,
        address _collateral
    ) public returns (uint256) {
        address xtoken = poolConfiguration.underlyingAssetToXtoken(_asset);
        address debtToken = poolConfiguration.underlyingAssetToDebtToken(
            _asset
        );
        address collateralXToken = poolConfiguration.underlyingAssetToXtoken(
            _collateral
        );

        (bool isValid, uint256 amountOfCollateral) = poolLogic.validateBorrow(
            msg.sender,
            _asset,
            _amount,
            _collateral
        );

        if (!isValid) {
            return 0;
        } else {
            IXToken(xtoken).transferUnderlyingAssetTo(msg.sender, _amount);
            IXToken(collateralXToken).burn(msg.sender, amountOfCollateral);

            IDebtToken(debtToken).mint(msg.sender, _amount);

            reservesManager.updateState(_asset, _amount, 1);
            userToBorrowedAssetToCollateral[msg.sender][_asset] = _collateral;
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
            reservesManager.updateState(_asset, _amount, 2);
            userToCollateralToAmount[msg.sender][_asset] =
                userToCollateralToAmount[msg.sender][_asset] -
                _amount;

            return _amount;
        }
    }

    function repay(address _asset, uint256 _amount) public {
        require(_amount > 0, "insufficient amount");
        require(poolConfiguration.isAvailable(_asset), "token not available");
        address debtToken = poolConfiguration.underlyingAssetToDebtToken(
            _asset
        );
        require(
            IERC20(debtToken).balanceOf(msg.sender) > 0,
            "doesnt have a debt to pay"
        );

        require(
            _amount <= IERC20(debtToken).balanceOf(msg.sender),
            "the amount exceeds the debt"
        );

        address collateral = userToBorrowedAssetToCollateral[msg.sender][
            _asset
        ];

        address asset_xtoken = poolConfiguration.underlyingAssetToXtoken(
            _asset
        );
        address collateral_xtoken = poolConfiguration.underlyingAssetToXtoken(
            collateral
        );
        IERC20(_asset).transferFrom(msg.sender, asset_xtoken, _amount);
        IXToken(collateral_xtoken).mint(
            msg.sender,
            poolLogic.getCollateralAmountToMint(_asset, _amount, collateral)
        );
        IDebtToken(debtToken).burn(msg.sender, _amount);
        reservesManager.updateState(_asset, _amount, 3);
    }

    function liquidationCall(
        address _user,
        address _asset,
        uint256 _amount,
        address _collateral
    ) public returns (bool) {
        require(_amount > 0, "insufficient amount");
        require(poolConfiguration.isAvailable(_asset), "token not available");
        require(
            poolConfiguration.isAvailable(_collateral),
            "token not available"
        );
        (bool isValid, uint256 undercollateralizedAmount) = poolLogic
            .validateLiquidation(
                _user,
                _asset,
                _collateral,
                userToCollateralToAmount[_user][_collateral]
            );

        if (!isValid) {
            return false;
        } else {
            require(
                _amount <= undercollateralizedAmount,
                "amount exceeds undercollateralized amount"
            );
            address asset_xtoken = poolConfiguration.underlyingAssetToXtoken(
                _asset
            );
            address collateral_xtoken = poolConfiguration
                .underlyingAssetToXtoken(_collateral);
            address debtToken = poolConfiguration.underlyingAssetToDebtToken(
                _asset
            );
            IERC20(_asset).transferFrom(msg.sender, asset_xtoken, _amount);
            IXToken(collateral_xtoken).mint(msg.sender, _amount);
            IDebtToken(debtToken).burn(_user, _amount);

            return true;
        }
    }
}
