import TrustIndex as TI 

class Record:
	def __init__(self, timestamp, txid, source, destination, updateid, chain):
		self.timestamp = timestamp
		self.txid = txid
		self.source = source
		self.destination = destination
		self.updateid = updateid
		self.chain = chain

	def toString(self):
		return("Timestamp: {0} - TXID: {1} - Updateid: {2} - Chain: {3}".format(self.timestamp, self.txid, self.updateid, self.chain))	



# import networkx as nx 
# import matplotlib.pyplot as plt


# testcaseGraph = nx.DiGraph()
# testcaseGraph.add_edge("A", "B")
# testcaseGraph.add_edge("A", "C")
# testcaseGraph.add_edge("C", "A")
# testcaseGraph.add_edge("B", "D")
# testcaseGraph.add_edge("C", "B")
# testcaseGraph.add_edge("D", "C")
# testcaseGraph.add_edge("C", "D")
# seedset = ["C"]

# ATR = TI.AntiTrustRank(testcaseGraph, seedset)

# print(ATR)


# nx.draw(testcaseGraph, with_labels=True)
# plt.savefig("./network2.png")


defaultUID = '0000000000000000000000000000000000000000000000000000000000000000'
record1 = Record(1,"1","","",defaultUID,0)
record2 = Record(2,"2","","","1",0)
record3 = Record(3,"3","","","1",0)
record4 = Record(4,"4","","","2",0)
record5 = Record(5,"5","","","3",0)
record6 = Record(6,"6","","","5",0)
record7 = Record(7,"7","","","5",0)
record8 = Record(8,"8","","","7",0)
record9 = Record(9,"9","","","7",0)
record10 = Record(10,"10","","",defaultUID,0)
record11 = Record(11,"11","","","10",0)


testcase = [record1, record2, record3, record4, record5, record6, record7, record8, record9, record10, record11]
updateIDList = ["1", "2", "3", "5", "7", "10"]
List = TI.RemoveOldRecords(testcase, updateIDList)
record9 = Record(9,"9","","","1",3)
expected = [record9, record11]

for x in List:
	print(x.toString())

for y in expected:
	print(y.toString())

print(len(List))
print(len(expected))

def record_comparison(testcase, expected):
	if len(testcase) != len(expected): return False 
	print("x")
	for y in range(len(testcase)):
		if (testcase[y].timestamp != expected[y].timestamp) and (testcase[y].txid != expected[y].txid): return False
		if (testcase[y].updateid != expected[y].updateid): return False
	return True

print(record_comparison(List, expected))
