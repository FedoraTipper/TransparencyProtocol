import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

#ABI for smart contract
import contract_abi
from web3 import Web3, HTTPProvider

defaultUID = '0000000000000000000000000000000000000000000000000000000000000000'

class Record:
	def __init__(self, timestamp, txid, source, destination, updateid, payload, chain):
		self.timestamp = timestamp
		self.txid = txid.hex()
		self.source = source
		self.updateid = updateid.hex()
		self.destination = destination
		self.payload = payload
		self.chain = chain

	def toString(self):
		return("Timestamp: {0} - TXID: {1} - Source: {2} Destination: {3} - Updateid: {4} - Payload: {5} - Chain: {6}".format(self.timestamp, self.txid, self.source, self.destination, self.updateid, self.payload, self.chain))

def PopulateRecordList(IDList):
	RecordList = list()
	UpdateIDList = list()
	#Load all records
	for txid in IDList:
		result = contract.functions.getRecord(txid).call()
		record = Record(result[0], txid, result[1], result[2], result[3], result[4], 0)
		RecordList.append(record)
		if result[3].hex() != defaultUID:
			UpdateIDList.append(result[3].hex())
	return (RecordList, UpdateIDList)

def initGraph(RecordList):
	G = nx.DiGraph()
	for record in RecordList:
		G.add_edge(str(record.source), str(record.destination))
	return G

def RemoveOldRecords(RecordList, UpdateIDList):
	RecordList, chainHash, timestampHash = InitialRemoveRecords(RecordList, UpdateIDList)
	if(len(chainHash) + len(timestampHash) != 0):
		RecordList = RemoveConditionalRecords(RecordList, chainHash, timestampHash)
	return RecordList

def InitialRemoveRecords(RecordList, UpdateIDList):
	offset = 0
	chainHash = {}
	timestampHash = {}
	tempList = list(RecordList)
	for x in range(len(RecordList)):
		if RecordList[x].txid in UpdateIDList:
			if(RecordList[x].updateid != defaultUID):
				highestChain, oldest = UpdateIDs(RecordList[x].txid, RecordList[x].updateid, RecordList[x].chain, tempList)
				chainHash[RecordsList[x].updateid] = highestChain
				timestampHash[RecordList[x].updateid] = oldest
			tempList.pop(x - offset)
			offset = offset + 1
	return tempList, chainHash, timestampHash

def RemoveConditionalRecords(RecordList, chainHash, timestampHash):
	offset = 0
	tempList = list(RecordList)
	for x in range(len(RecordList)):
		if RecordList[x].updateid != defaultUID and (chainHash[RecordList[x].updateid] > RecordList[x].chain or timestampHash[RecordList[x].updateid] > RecordList[x].timestamp):
			tempList.pop(x - offset)
			offset = offset + 1
	return tempList

def UpdateIDs(oldUID, newUID, chain, RecordList):
	highestChain = -1
	oldest = -1
	for y in range(len(RecordList)):
		if RecordList[y].updateid == oldUID:
			RecordList[y].updateid = newUID
			RecordList[y].chain = chain + 1
			highestChain = RecordList[y].chain if RecordList[y].chain > highestChain else highestChain
			oldest = RecordList[y].timestamp if RecordList[y].timestamp > oldest else oldest
	return highestChain, oldest


def InDegreeList(G,	PRList, keyNode):
	inDegreeList = list()
	for node in PRList:
		outDegreeHash = G[node]
		inDegreeList.append(node) if keyNode in outDegreeHash else InDegreeList
	return inDegreeList

#d: dampening factor
#G: digraph of records
#epsilon: error of v
def PageRank(G, d = 0.85, epsilon = 1.0e-8):
	PRList = list(G.nodes())
	N = G.number_of_nodes()

	M = np.array([[0.0 for x in range(N)] for y in range(N)])
	Ones = np.array([[1.0 for x in range(N)] for y in range(N)])
	v = np.array([1/N for x in range(N)])

	for node in PRList:
		nodeIndex = PRList.index(node)
		inDegreeList = InDegreeList(G, PRList, node)
		for indegree in inDegreeList:
			indegreeIndex = PRList.index(indegree)
			M[nodeIndex][indegreeIndex] = 1 / G.out_degree(indegree)

	#Simplification: M_hat = dM + (1-d)/N
	M_hat = (d * M) + (((1-d)/N) * Ones)
	last_v = Ones[0]

	while np.linalg.norm(v - last_v, 2) > epsilon:
		last_v = v
		v = np.matmul(M_hat, v)

	return (v, PRList)

# web3.py instance
w3 = Web3(HTTPProvider("https://ropsten.infura.io/v3/e3edb56114244a31b698dd92dc7cfcf7", request_kwargs={'timeout': 60}))

contract = w3.eth.contract(
    address = "0x49E8410Bf14C42398e16A91bF75d2e930893B447",
    abi = contract_abi.abi
)

#Display the default greeting from the contract
IDList = contract.functions.getRecordIDs().call()

RecordList, UpdateIDList = PopulateRecordList(IDList)

for x in RecordList:
	print(x.toString())

RecordList = RemoveOldRecords(RecordList, UpdateIDList)

print("						")
for x in RecordList:
	print(x.toString())

G = initGraph(RecordList)

PRv, PRList = PageRank(G)

print(PRv)

sum1 = 0
for x in range(len(PRv)):
	sum1 = sum1 + PRv[x]
print(sum1)

nx.draw(G, with_labels=True)
plt.show()