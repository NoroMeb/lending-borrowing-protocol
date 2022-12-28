// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

import "./../ReservesManager.sol";

import "@ds-math/src/math.sol";

contract DebtToken is ERC20, DSMath {
    address public poolAddress;
    address public underlyingAsset;

    ReservesManager public reservesManager;

    modifier onlyPool() {
        require(_msgSender() == poolAddress, "caller must be pool");
        _;
    }

    constructor(
        string memory _name,
        string memory _symbol,
        address _underlyingAsset,
        address _poolAddress,
        address _reservesManagerAddress
    ) ERC20(_name, _symbol) {
        poolAddress = _poolAddress;
        underlyingAsset = _underlyingAsset;
        reservesManager = ReservesManager(_reservesManagerAddress);
    }

    function mint(address _account, uint256 _amount) external onlyPool {
        super._mint(_account, _amount);
    }

    function burn(address _account, uint256 _amount) external onlyPool {
        super._burn(_account, _amount);
    }

    function transfer(address recipient, uint256 amount)
        public
        virtual
        override
        returns (bool)
    {
        recipient;
        amount;
        revert("TRANSFER_NOT_SUPPORTED");
    }

    function allowance(address owner, address spender)
        public
        view
        virtual
        override
        returns (uint256)
    {
        owner;
        spender;
        revert("ALLOWANCE_NOT_SUPPORTED");
    }

    function approve(address spender, uint256 amount)
        public
        virtual
        override
        returns (bool)
    {
        spender;
        amount;
        revert("APPROVAL_NOT_SUPPORTED");
    }

    function transferFrom(
        address sender,
        address recipient,
        uint256 amount
    ) public virtual override returns (bool) {
        sender;
        recipient;
        amount;
        revert("TRANSFER_NOT_SUPPORTED");
    }

    function increaseAllowance(address spender, uint256 addedValue)
        public
        virtual
        override
        returns (bool)
    {
        spender;
        addedValue;
        revert("ALLOWANCE_NOT_SUPPORTED");
    }

    function decreaseAllowance(address spender, uint256 subtractedValue)
        public
        virtual
        override
        returns (bool)
    {
        spender;
        subtractedValue;
        revert("ALLOWANCE_NOT_SUPPORTED");
    }

    function balanceOf(address user)
        public
        view
        virtual
        override
        returns (uint256)
    {
        uint256 scaledBalance = super.balanceOf(user);

        if (scaledBalance == 0) {
            return 0;
        }

        return
            wmul(
                scaledBalance,
                reservesManager.getVariableBorrowIndexSinceLastUpdate(
                    underlyingAsset
                )
            );
    }
}
