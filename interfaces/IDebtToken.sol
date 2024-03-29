// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface IDebtToken is IERC20 {
    function mint(address _account, uint256 _amount) external;

    function burn(address _account, uint256 _amount) external;

    function getTotalBorrowed() external view returns (uint256);

    function setTotalBorrowed(uint256 _totalBorrowed) external;
}
