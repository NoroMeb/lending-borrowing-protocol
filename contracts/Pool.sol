// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "./PoolLogic.sol";
import "./PoolConfiguration.sol";
import "./ReservesManager.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IXToken.sol";
import "../interfaces/IDebtToken.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @author  . MEBARKIA Abdenour
 * @title   . Pool Contract
 * @dev     . Main point of interaction with the protocol, users can :
 *               . supply
 *               . borrow
 *               . withdraw
 *               . repay
 *               . liquidate undercollateralized user
 */

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

    /**
     * @notice  . Deposits an `amount` of underlying asset into the reserve, receiving in return overlying xTokens.
     * - E.g. User deposits 100 USDC and gets in return 100 xUSDC
     * @param   _asset  . The address of the underlying asset to deposit .
     * @param   _amount  . The amount to be deposited .
     */
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

    /**
     * @notice  . Allows users to borrow a specific `amount` of the reserve underlying asset, provided that the borrower
     * already deposited enough collateral receiving in return debt Tokens .
     * @param   _asset  . The address of the underlying asset to borrow
     * @param   _amount  . The amount to be borrowed
     * @param   _collateral  . The address of the underlying asset to set as collateral (user should have already supplied enough amount of collateral )
     * @return  uint256  . the amount borrowed if the borrow function successfully executed otherwise it returns 0
     */
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

    /**
     * @notice  . Withdraws an `amount` of underlying asset from the reserve, burning the equivalent xTokens owned
     * E.g. User has 100 aUSDC, calls withdraw() and receives 100 USDC, burning the 100 xUSDC
     * @param   _asset  . The address of the underlying asset to withdraw
     * @param   _amount  . The underlying amount to be withdrawn
     * @return  uint256  . the amount withdrawn if the withdraw function successfully executed otherwise it returns 0
     */
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

    /**
     * @notice  . Repays a borrowed `amount` , burning the equivalent debt tokens owned
     * @param   _asset  . The address of the borrowed underlying asset previously borrowed
     * @param   _amount  . The amount to repay
     */
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

    /**
     * @notice  . Function to liquidate a non-healthy position collateral-wise
     * @param   _user  . The address of the borrower getting liquidated
     * @param   _asset  . The address of the underlying borrowed asset to be repaid with the liquidation
     * @param   _amount  . The debt amount of borrowed `asset` the liquidator wants to cover
     * @param   _collateral  . The address of the underlying asset used as collateral, to receive as result of the liquidation
     * @return  bool  . succes boolian .
     */
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
                _collateral
            );
            IERC20(_asset).transferFrom(msg.sender, asset_xtoken, _amount);
            IXToken(collateral_xtoken).mint(msg.sender, _amount);
            IDebtToken(debtToken).mint(_user, _amount);

            return true;
        }
    }
}
