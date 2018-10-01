import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import sqlalchemy

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
	for x, record in enumerate(RecordList):
		if record.txid in UpdateIDList:
			if(record.updateid != defaultUID):
				highestChain, oldest = UpdateIDs(record.txid, record.updateid, record.chain, tempList)
				chainHash[record.updateid] = highestChain
				timestampHash[record.updateid] = oldest
			tempList.pop(x - offset)
			offset = offset + 1
	return tempList, chainHash, timestampHash

def RemoveConditionalRecords(RecordList, chainHash, timestampHash):
	offset = 0
	tempList = list(RecordList)
	for x, record in enumerate(RecordList):
		if record.updateid != defaultUID and (chainHash[record.updateid] > record.chain or timestampHash[record.updateid] > record.timestamp):
			tempList.pop(x - offset)
			offset = offset + 1
	return tempList

def UpdateIDs(oldUID, newUID, chain, RecordList):
	highestChain = -1
	oldest = -1
	for record in RecordList:
		if record.updateid == oldUID:
			record.updateid = newUID
			record.chain = chain + 1
			highestChain = record.chain if record.chain > highestChain else highestChain
			oldest = record.timestamp if record.timestamp > oldest else oldest
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

	for nodeIndex, node in enumerate(PRList):
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
    address = "0xD946eddE77A7486321D9445EC78f7b1ea0B9EA53",
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

rankHash = {}
for i, rank in enumerate(PRv):
	rankHash[PRList[i]] = rank

sorted_items = sorted(rankHash.items(), key=lambda x: x[1])

sum1 = 0
for x in range(len(PRv)):
	sum1 = sum1 + PRv[x]
print(sum1)


def SaveRanks(sortedRankHash):
	con, meta = connect('main2', 'test1234', 'pagerankdb')

	clean_ranks = "DELETE FROM rank"
	query = con.execute(clean_ranks)

	for count, key in enumerate(rankHash):
		statement = "INSERT INTO rank (pub_key, rank) VALUES ('%s', %d)" % (key, (count + 1))
		count = count + 1
		query = con.execute(statement)


def connect(user, password, db, host='178.128.43.198', port=5432):
    '''Returns a connection and a metadata object'''
    # We connect with the help of the PostgreSQL URL
    # postgresql://federer:grandestslam@localhost:5432/tennis
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)

    # The return value of create_engine() is our connection object
    con = sqlalchemy.create_engine(url, client_encoding='utf8')

    # We then bind the connection to MetaData()
    meta = sqlalchemy.MetaData(bind=con, reflect=True)

    return con, meta

SaveRanks(sorted_items)

nx.draw(G, with_labels=True)
plt.show()