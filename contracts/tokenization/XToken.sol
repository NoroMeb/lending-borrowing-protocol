// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract XToken is ERC20 {
    address poolAddress;
    modifier onlyPool() {
        require(_msgSender() == poolAddress, "caller must be pool");
        _;
    }

    constructor(
        string memory _name,
        string memory _symbol,
        address _poolAddress
    ) public ERC20(_name, _symbol) {
        poolAddress = _poolAddress;
    }

    function mint(address _account, uint256 _amount) external onlyPool {
        _mint(_account, _amount);
    }
}
