import TrustIndex as TI
import networkx as nx
import matplotlib.pyplot as plt

#ABI for smart contract
import contract_abi
from web3 import Web3, HTTPProvider


class Record:
	def __init__(self, timestamp, txid, source, destination, updateid, payload, chain):
		self.timestamp = timestamp
		self.txid = txid
		self.source = source
		self.updateid = updateid
		self.destination = destination
		self.payload = payload
		self.chain = chain

	def toString(self):
		return("Timestamp: {0} - TXID: {1} - Source: {2} Destination: {3} - Updateid: {4} - Payload: {5} - Chain: {6}".format(self.timestamp, self.txid, self.source, self.destination, self.updateid, self.payload, self.chain))

record1 = Record(1,"1","A","B","0","",0)
record2 = Record(2,"2","A","C","0","",0)
record3 = Record(3,"3","C","A","0","",0)
record4 = Record(4,"4","B","D","0","",0)
record5 = Record(5,"5","C","B","0","",0)
record6 = Record(6,"6","D","C","0","",0)
record7 = Record(7,"7","C","D","0","",0)
record8 = Record(8,"8","E","B","0","F",0)
#record9 = Record(8,"8","E","A","0","F",0)

#record8 = Record(8,"8","E","G","0","",0)
#record9 = Record(9,"9","G","H","0","",0)
#record10 = Record(10,"10","H","A","0","",0)

authNode  = [str(record8.source)]
list2 = [record1, record2, record3, record4, record5, record6, record7, record8]
RecordList = list()
UpdateIDList = list()

for txid in list2:
	#result = contract.functions.getRecord(txid).call()
	#record = Record(result[0], txid, result[1], result[2], result[3], result[4])
	RecordList.append(txid)
	#if result[3].hex() != '0000000000000000000000000000000000000000000000000000000000000000':
	#	UpdateIDList.append(result[3].hex())
	if txid.updateid != '0':
		UpdateIDList.append(txid.updateid)

for x in RecordList:
	print(x.toString())

RecordList = TI.RemoveOldRecords(RecordList, UpdateIDList)

print("						")
for x in RecordList:
	print(x.toString())

G, markedNodes = TI.initAntiTrustGraph(RecordList, "F", authNode)

# webg = nx.to_numpy_matrix(G)
# print(webg)
# T = webg.transpose()
# print(T)


# print(markedNodes)

# print(list(G.neighbors("A")))
# print(list(G.neighbors("A")) in markedNodes)

antiRankHash = TI.AntiTrustRank(G, markedNodes)

anti_sorted_items = sorted(antiRankHash.items(), key=lambda x: x[1])

print(anti_sorted_items)

PRv, PRList = TI.PageRank(G)

rankHash = {}
for i, rank in enumerate(PRv):
	rankHash[PRList[i]] = rank

sorted_items = sorted(rankHash.items(), key=lambda x: x[1])

print(sorted_items)

# PRv, PRList = TI.PageRank(G)

# rankHash = {}
# for i, rank in enumerate(PRv):
# 	rankHash[PRList[i]] = rank

# sorted_items = sorted(rankHash.items(), key=lambda x: x[1])

# TI.SaveRanks(sorted_items)

# nx.draw(G, with_labels=True)
# plt.savefig("./network.png")
# plt.show()
