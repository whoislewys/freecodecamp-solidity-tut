from brownie import (
    accounts,
    network,
    config,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    Contract,
    interface,
)

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

def get_account(index=None, id=None):
    # accounts[0]
    # accounts.add("env")
    # accounts.load("id")
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    print('get acct testnet getting wallet from key: ', config["wallets"]["from_key"])
    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
  """Grab contract addrs from brownie config
  if defined, otherwise deploy mock
  
  For example, on a mainnet fork environment a WETH contract will exist. On a mock development chain, it will not.

    Args:
      contract_name (string)

    Returns:
      brownie.network.contract.ProjectContract: The most recently deployed v of this contract
  """
  contract_type = contract_to_mock[contract_name]
  if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
    if len(contract_type) <= 0:
      # check if there are any deployed contracts of type contract_type
      # if no, deploy mocks
      deploy_mocks()
    # get most recently deployed contract of type `contract_type`
    contract = contract_type[-1] 
  else:
    # if mainnet or testnet, instantiate the contract. requires address, ABI
    contract_address = config['networks'][network.show_active()][contract_name]
    contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)
  return contract

DECIMALS = 8
INITIAL_VALUE = 200000000000

def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
  account = get_account()
  MockV3Aggregator.deploy(
    decimals, initial_value, {'from': account}
  )
  link_token = LinkToken.deploy({'from': account})
  VRFCoordinatorMock.deploy(link_token.address, {'from': account})
  print('Deployed mocks!')


def fund_with_link(contract_address, account=None, link_token=None, amount=100000000000000000): #0.1 link
  account = account if account else get_account()
  link_token = link_token if link_token else get_contract('link_token')

  print(f'funding contract addr {contract_address} with {amount} link | from account: {account}!')

  # can create contract from ABI & address and interact with it that way
  tx = link_token.transfer(contract_address, amount, {'from': account})
  tx.wait(1)

  # can also interact with it JUST via the interface, brownie will compile it down to abi for u
  # link_token_contract = interface.LinkTokenInterface(link_token.address)
  # tx = link_token_contract.transfer(contract_address, amount, {'from': account})
  # tx.wait(1)

  print(f'funded contract addr {contract_address} w/ some link!')
  return tx











