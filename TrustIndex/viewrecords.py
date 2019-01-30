#ABI for smart contract
import contract_abi
from web3 import Web3, HTTPProvider

# Load web3.py instance
w3 = Web3(HTTPProvider("https://ropsten.infura.io/v3/e3edb56114244a31b698dd92dc7cfcf7", request_kwargs={'timeout': 60}))
contract = w3.eth.contract(
    address = "0x7e55ebD9C7b6aA3b63D1A303e61FF11472E16F76",
    abi = contract_abi.abi
)

IDList = contract.functions.getRecordIDs().call()


for x in IDList:
	print(x.hex())