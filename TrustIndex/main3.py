import TrustIndex as TI
import networkx as nx
import matplotlib.pyplot as plt

#ABI for smart contract
import contract_abi
from web3 import Web3, HTTPProvider


# web3.py instance
w3 = Web3(HTTPProvider("https://ropsten.infura.io/v3/e3edb56114244a31b698dd92dc7cfcf7", request_kwargs={'timeout': 60}))

contract = w3.eth.contract(
    address = "0xD946eddE77A7486321D9445EC78f7b1ea0B9EA53",
    abi = contract_abi.abi
)

#Display the default greeting from the contract
IDList = contract.functions.getRecordIDs().call()

RecordList, UpdateIDList = TI.PopulateRecordList(IDList, contract)

for x in RecordList:
	print(x.toString())

RecordList = TI.RemoveOldRecords(RecordList, UpdateIDList)

print("						")
for x in RecordList:
	print(x.toString())

G = TI.initGraph(RecordList)

PRv, PRList = TI.PageRank(G)

rankHash = {}
for i, rank in enumerate(PRv):
	rankHash[PRList[i]] = rank

sorted_items = sorted(rankHash.items(), key=lambda x: x[1])

TI.SaveRanks(sorted_items)

nx.draw(G, with_labels=True)
plt.savefig("./network.png")
plt.show()
