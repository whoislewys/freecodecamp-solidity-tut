## Completed Repo
https://github.com/PatrickAlphaC/aave_brownie_py_freecode/blob/main/interfaces/IWeth.sol


## TODOs
1. Get weth
2. Deposit ETH into Aave
3. Borrow some asset with the ETH collateral
    1. [optionsl] Sell the borrowed asset
4. Repay loan

Testing

Integration test, do on kovan bc aave has testnet - noice

Local unit test? how tf. (this is the problem i ran into trying to fuck with dopex. fork mainnet somehow? what about the different states the contract can exist in tho)

AH yes he said we will unit test with mainnet-fork

Ruel of thumb: 
If you're notusing oracles, and you don't need to mock responses, you can just use a mainnet fork to run unit tests

If you ARE using oracles, it makes more sense to use a development network where you can mock oracles & responses



