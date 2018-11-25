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

def PopulateRecordList(IDList, contract):
	RecordList = list()
	UpdateIDList = list()
	#Load all records
	for txid in IDList:
		result = contract.functions.getRecord(txid).call()
		record = Record(result[0], txid, result[1], result[2], result[3], result[4], 0)
		RecordList.append(record)
		if result[3].hex() != defaultUID:
			if (result[3].hex() not in UpdateIDList):
				UpdateIDList.append(result[3].hex())
	return (RecordList, UpdateIDList)

def RemoveOldRecords(RecordList, UpdateIDList):
	RecordList, chainHash, timestampHash = InitialRemoveRecords(RecordList, UpdateIDList)
	if(len(chainHash) + len(timestampHash) != 0):
		RecordList = RemoveConditionalRecords(RecordList, chainHash, timestampHash)
	return RecordList

def InitialRemoveRecords(RecordList, UpdateIDList, chainHash = {}, timestampHash = {}, offset = 0):
	tempList = list(RecordList)
	for x, record in enumerate(RecordList):
		if record.txid in UpdateIDList:
			if(record.updateid != defaultUID):
				highestChain, oldest = UpdateIDs(record.txid, record.updateid, record.chain, tempList)
				chainHash[record.updateid] = highestChain
				timestampHash[record.updateid] = oldest
			else: 
				chainHash[record.txid] = record.chain 
				timestampHash[record.txid] = record.timestamp
			tempList.pop(x - offset)
			offset = offset + 1
	return tempList, chainHash, timestampHash

def RemoveConditionalRecords(RecordList, chainHash, timestampHash, offset = 0):
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


def initGraph(RecordList):
	G = nx.DiGraph()
	for record in RecordList:
		G.add_edge(str(record.source), str(record.destination))
	return G

def initAntiTrustGraph(RecordList, PayloadID, AuthorityNodeList):
	markedNodes = list()
	G = nx.DiGraph()
	for record in RecordList:
		if str(record.payload) == PayloadID and str(record.source.lower()) in AuthorityNodeList:
			markedNodes.append(str(record.destination))
		else:
			G.add_edge(str(record.source), str(record.destination))	
	return G, markedNodes

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

	#Normalise ranks until error limit is reached
	while np.linalg.norm(v - last_v, 2) > epsilon:
		last_v = v
		v = np.matmul(M_hat, v)

	rankHash = {}
	for i, rank in enumerate(v):
		rankHash[PRList[i]] = rank	

	return rankHash

def AntiTrustRank(G, SeedSet, decay = 0.55):
	PRList = list(G.nodes())
	N = G.number_of_nodes()

	#Generate Binary webgraph matrix
	binMatrix = nx.to_numpy_matrix(G)
	T = binMatrix.transpose()
	TArray = np.squeeze(np.asarray(T))

	A = np.array([[0.0 for x in range(N)] for y in range(N)])

	for i in range(N):
		for j in range(N):
			A[i][j] = decay * TArray[i][j] + ((1-decay)/len(SeedSet)) if connects_to_seedset(G.neighbors(PRList[i]), SeedSet) else decay * TArray[i][j]

	antiRankHash = {}
	for index, i in enumerate(A):
		temp = 0
		for j in i:
			temp = temp + j
		antiRankHash[PRList[index]] = temp

	return antiRankHash

def connects_to_seedset(neighbors, SeedSet):
	for node in neighbors:
		if node in SeedSet: return True
	return False 

def SaveRanks(rankList, ATR):
	con = connect('main2', 'test1234', '178.128.43.198', '5432', 'pagerankdb')

	clean_ranks = "DELETE FROM rank"
	query = con.execute(clean_ranks)

	if ATR == 0:
		for count, key in enumerate(rankList):
			statement = "INSERT INTO rank (pub_key, rank) VALUES ('%s', %d)" % (key[0], (count + 1))
			query = con.execute(statement)
	else:
		for i in range(len(rankList)):
			statement = "INSERT INTO rank (pub_key, rank, at_rank, seedset) VALUES ('%s', %d, %d, %d)" % (rankList[i][0], (i + 1), rankList[i][2], rankList[i][3])
			query = con.execute(statement)

	#Close connection with database
	con.dispose()


def connect(username, password, ip, port, dbName):
	url = "postgresql://%s:%s@%s:%s/%s" % (username, password, ip, port, dbName)
	con = sqlalchemy.create_engine(url)
	return con
