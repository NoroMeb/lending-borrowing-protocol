pragma solidity ^0.8.12;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract LinkTokenMock is ERC20 {
    constructor() public ERC20("Mock LINK", "LINK") {
        _mint(msg.sender, 100000 * 10**18);
    }
}
