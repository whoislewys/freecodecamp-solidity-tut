from brownie import Lottery, accounts, config, network, exceptions
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import INITIAL_VALUE, LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, fund_with_link, get_contract
from web3 import Web3
import pytest


def test_get_entrance_fee():
  if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
    pytest.skip()

  # Arrange
  lottery = deploy_lottery()

  # Act
  
  entrance_fee = lottery.getEntranceFee()

  # Assert
  expected_entrance_fee = Web3.toWei(50 / INITIAL_VALUE * 10e7, 'ether')
  assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
  # Arrage
  if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
    pytest.skip()

  #Act/assert
  lottery = deploy_lottery()
  with pytest.raises(exceptions.VirtualMachineError):
    lottery.enter({'from': get_account(), 'value': lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
  # Arrange
  if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
    pytest.skip()
  lottery = deploy_lottery()
  account = get_account()
  lottery.startLottery({'from': account})

  lottery.enter({'from': account, 'value': lottery.getEntranceFee()})

  assert lottery.players(0) == account


def test_can_end_lottery():
  # Arrange
  if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
    pytest.skip()

  lottery = deploy_lottery()
  account = get_account()
  lottery.startLottery({'from': account})
  lottery.enter({'from': account, 'value': lottery.getEntranceFee()})
  fund_with_link(lottery.address) # remember, endlottery needs contract to have link for chainlink VRF request
  
  lottery.endLottery({'from': account})

  assert lottery.lotteryState() == 2


def test_can_pick_winner_correctly():
  # Arrange
  if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
    pytest.skip()

  lottery = deploy_lottery()
  account = get_account()
  lottery.startLottery({'from': account})
  accounts = [account, get_account(index=1), get_account(index=2)]
  for acc in accounts:
    lottery.enter({'from': acc, 'value': lottery.getEntranceFee()})

  initialLotteryBalance = lottery.balance()

  # get winner and their starting balance given a dummy rng value
  dummyRandomness = 69
  expectedWinnerIdx = dummyRandomness % len(accounts)
  expectedWinnerStartingBalance = accounts[expectedWinnerIdx].balance()

  # Act
  # make sure you have some local brownie accounts for this. `brownie accounts generate <id>`
  # you find more: https://eth-brownie.readthedocs.io/en/stable/account-management.html#local-accounts
  fund_with_link(lottery.address) # remember, endlottery needs contract to have link for chainlink VRF request
  # Mock the randomness call...
  # get the request id off the endlottery event it emits,
  # so that we can use it to mimic the chainlink node calling  VRFCoordinatorMock.callbackWithRandomness, which will call fulfillRandomness in our lotto contract
  endtx = lottery.endLottery({'from': account})
  reqid = endtx.events['RequestedRandomness']['requestId']
  get_contract('vrf_coordinator').callBackWithRandomness(reqid, dummyRandomness, lottery.address)

  # Asset
  assert lottery.recentWinner() == accounts[expectedWinnerIdx]
  assert accounts[expectedWinnerIdx].balance() == expectedWinnerStartingBalance + initialLotteryBalance
