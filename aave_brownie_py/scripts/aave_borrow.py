from brownie import network, config, interface, Contract
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth

def main():
  account = get_account()
  erc20_address = config['networks'][network.show_active()]['weth_token']

  if network.show_active() in ['mainnet-fork']:
    # get weth if no weth (local env)
    # make sure you got weth in your respective testnet if running in testnet
    get_weth()

  # how to lend? look docs....
  # https://docs.aave.com/developers/the-core-protocol/protocol-overview

  # lendingp ool contract
  # u know the drill... get ABI, Address
  lending_pool = get_lending_pool()


def get_lending_pool():
  # aave has a contract that gives the addresses of their various lending pool contracts
  lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(config['networks'][network.show_active()]['lending_pool_addresses_provider'])

  # got lending pool addr...
  # now we need lending pool abi (can get from interface on aave github)
  lending_pool_address = lending_pool_addresses_provider.getLendingPool()
  lending_pool = interface.ILendingPool(lending_pool_address)
  return lending_pool

