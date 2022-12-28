// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

import "./../ReservesManager.sol";

import "@ds-math/src/math.sol";

contract XToken is ERC20, DSMath {
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

    function transferUnderlyingAssetTo(address _account, uint256 _amount)
        external
        onlyPool
    {
        IERC20(underlyingAsset).transfer(_account, _amount);
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
                reservesManager.getSupplyIndexSinceLastUpdate(underlyingAsset)
            );
    }
}
