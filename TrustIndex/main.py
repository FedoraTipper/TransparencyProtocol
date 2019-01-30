import TrustIndex as TI
import networkx as nx
import matplotlib.pyplot as plt
import time
import sys
from datetime import datetime

#ABI for smart contract
import contract_abi
from web3 import Web3, HTTPProvider

# Load web3.py instance
w3 = Web3(HTTPProvider("https://ropsten.infura.io/v3/e3edb56114244a31b698dd92dc7cfcf7", request_kwargs={'timeout': 60}))
contract = w3.eth.contract(
    address = "0xD946eddE77A7486321D9445EC78f7b1ea0B9EA53",
    abi = contract_abi.abi
)

def main(ATR, PayloadID, seconds = 300):
	previous = 0
	while(1):
		TotalRecords = contract.functions.getRecordNumber()
		if previous != TotalRecords:
			print("%s - Starting update" % datetime.now().strftime('%m-%d %H:%M:%S')) 
			UpdateRecords(ATR, PayloadID)
			previous = TotalRecords
		else:
			#Sleep for 5 minutes
			print("%s - Sleeping (%d seconds)" % (datetime.now().strftime('%m-%d %H:%M:%S') ,seconds))
			time.sleep(seconds)


def UpdateRecords(ATR, PayloadID):
	#Display the default greeting from the contract
	IDList = contract.functions.getRecordIDs().call()

	RecordList, UpdateIDList = TI.PopulateRecordList(IDList, contract)
	RecordList = TI.RemoveOldRecords(RecordList, UpdateIDList)

	if(ATR == 1):
		authNodes = populateAuthNodes()
		print(authNodes)
		G, markedNodes = TI.initAntiTrustGraph(RecordList, PayloadID, authNodes)
		ATRankHash = TI.AntiTrustRank(G, markedNodes)
		rankHash = TI.PageRank(G)
		mergedRanks = mergeHash(rankHash, ATRankHash, markedNodes)
		print(mergedRanks)
		TI.SaveRanks(mergedRanks, 1)
	else:
		G = TI.initGraph(RecordList)
		rankHash = TI.PageRank(G)
		rankHash = sorted(rankHash.items(), key=lambda x: x[1])
		TI.SaveRanks(rankHash, 0)
		print(rankHash)

def mergeHash(rankHash, ATRankHash, markedNodes):
	merge = [[None for y in range(4)] for x in range(len(ATRankHash))]
	for i, node in enumerate(ATRankHash):
		merge[i][0] = node
		merge[i][1] = rankHash[node]
		merge[i][2] = ATRankHash[node]
		merge[i][3] = 1 if node in markedNodes else 0
	merge = sorted(merge, key=lambda x: x[2])
	for i in range(len(merge)):
		merge[i][2] = (i + 1)
	merge = sorted(merge, key=lambda x: x[1])
	return merge


def populateAuthNodes():
	with open("./Resources/authlist.txt", 'r') as authlist:
		return authlist.read().replace('\n', ' ').lower()


if(__name__ == "__main__"):
	if(len(sys.argv) > 1 and sys.argv[1] == "-a"):
		main(1, sys.argv[2])
	else:
		main(0, None)
