# Beginner-friendly decentralized lending borrowing protocol

## Description

This is a simple decentralized lending borrowing protocol built for nebies developers who try to understand how web3 lending platforms like _aave_ and _compound_ work .

## Main contracts

- **Pool**

  Main point of interaction with the protocol, users can :

  - supply
  - borrow
  - withdraw
  - repay
  - liquidate undercollateralized user

  as long as the token is supported by the protocol .

- **PoolConfiguration**

Allows the addition of a new token and all the related configuration .

- **PoolLogic**

Validate some end-user functions in the Pool contract .

- **ReservesManager**

Manage reserves and calculates debt & interests indexes .

## Interact with the protocol

You can deploy all contracts on goerli testnet and set all up by running the following command :

> brownie run scripts/arrange.py --network goerli

and then experiment with scripts in the `script` folder .

## Some resources that helped build this project

- [AAVE's developers documentation](https://docs.aave.com/developers/v/2.0/)
- [Compound documentation](https://docs.compound.finance/v2/)
- [Twitter thread](https://twitter.com/kinaumov/status/1535055544368906241)
- [Medium article](https://medium.com/coinmonks/how-to-code-a-lending-protocol-a9b5b021696d)
