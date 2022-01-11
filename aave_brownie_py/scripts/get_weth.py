from scripts.helpful_scripts import get_account
from brownie import interface, config, network


def main():
  get_weth()

def get_weth():
  '''
  Mints WETH by depositing ETH.
  Aave's weth gateway is a bigtime gas saver, but lets just do this the dumb way for learning
  '''
  '''
  important weth abi funcs:
    deposit: takes eth returns weth
    withdraw: takes weth, returns eth
  so, now we know what we need to call, let's go ahead and instantiate the contract

  We can instantiate a contract two ways:
  1. With ABI and address
  2. With the interface
  '''

  # question, how can i get the interface/ABI of a verified contract from etherscan?
  # etherscan has an api for this
  # you can also recreate the interface by hand. really, there's not a tool for this tho? whatever, ill just copy weth interafce from the project repo for now

  # ABI
  # Address

  # now that we have interface, we know we can compile it down to ABI
  account = get_account()
  print('acc: ', account)
  weth = interface.IWeth(config['networks'][network.show_active()]['weth_token'])
  tx = weth.deposit({'from': account, 'value': 0.05 * 10**18})
  print('Received weth')
  tx.wait(1) # wait for tx to finish, otherwise probs see (harmless) errors
  return tx
  
