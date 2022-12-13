// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract XToken is ERC20 {
    address public poolAddress;
    address public underlyingAsset;

    uint256 public totalDeposited;
    uint256 public totalBorrowed;

    modifier onlyPool() {
        require(_msgSender() == poolAddress, "caller must be pool");
        _;
    }

    constructor(
        string memory _name,
        string memory _symbol,
        address _underlyingAsset,
        address _poolAddress
    ) public ERC20(_name, _symbol) {
        poolAddress = _poolAddress;
        underlyingAsset = _underlyingAsset;
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

    function getTotalBorrowed() external view returns (uint256) {
        return totalBorrowed;
    }

    function setTotalBorrowed(uint256 _totalBorrowed) external onlyPool {
        totalBorrowed = _totalBorrowed;
    }

    function getTotalDeposited() external view returns (uint256) {
        return totalDeposited;
    }

    function setTotalDeposited(uint256 _totalDeposited) external onlyPool {
        totalDeposited = _totalDeposited;
    }
}
