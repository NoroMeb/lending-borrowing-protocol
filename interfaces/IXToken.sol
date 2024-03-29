// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface IXToken is IERC20 {
    function mint(address _account, uint256 _amount) external;

    function burn(address _account, uint256 _amount) external;

    function transferUnderlyingAssetTo(address _account, uint256 _amount)
        external;

    function getTotalDeposited() external view returns (uint256);

    function setTotalDeposited(uint256 _totalDeposited) external;
}
