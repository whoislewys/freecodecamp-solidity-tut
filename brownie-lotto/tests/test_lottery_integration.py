from brownie import Lottery, accounts, config, network, exceptions
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import INITIAL_VALUE, LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, fund_with_link, get_contract
from web3 import Web3
import pytest
import time

def test_can_pick_winner():
  # Arrange
  if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
    # don't run in devnet
    pytest.skip()
  lottery = deploy_lottery()
  print('entrance fee: ', lottery.getEntranceFee())
  account = get_account()
  print('init account balance: ', account.balance())
  lottery.startLottery({'from': account})
  accounts = [account, account]
  for acc in accounts:
    lottery.enter({'from': acc, 'value': lottery.getEntranceFee() + 1e10})

  # Act
  fund_with_link(lottery.address) # contract needs link for chainlink VRF request. 0.25 link
  endtx = lottery.endLottery({'from': account})
  # ghetto wait for rinkeby VRFCoordinator to call our fulfillRandomness impl
  time.sleep(60)

  # Assert
  print('recent winner: ', lottery.recentWinner())
  print('balance: ', lottery.balance())
  assert lottery.balance() == 0
  assert lottery.recentWinner() == account
