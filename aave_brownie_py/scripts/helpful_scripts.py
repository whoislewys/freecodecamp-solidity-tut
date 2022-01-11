from brownie import (
    accounts,
    network,
    config,
    Contract,
    interface,
)

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ['development', 'ganache-local',  'hardhat', 'mainnet-fork']

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    print('get acct testnet getting wallet from key: ', config["wallets"]["from_key"])
    return accounts.add(config["wallets"]["from_key"])
