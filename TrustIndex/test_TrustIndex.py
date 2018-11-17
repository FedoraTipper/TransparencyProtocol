import unittest
import TrustIndex as TI
import networkx as nx

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

class TestUpdate(unittest.TestCase):
	def setUp(self):
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
		self.expected = [record9, record11]
		self.updateIDList = ["1", "2", "3", "5", "7", "10"]
		self.testcase = [record1, record2, record3, record4, record5, record6, record7, record8, record9, record10, record11]
		self.testcase2 = [record1, record2, record3, record4, record5, record6, record7, record8, record9, record11]

	def test_removal(self):
		self.assertTrue(self.record_comparison(TI.RemoveOldRecords(self.testcase, self.updateIDList), self.expected))
		self.assertFalse(self.record_comparison(TI.RemoveOldRecords(self.testcase2, self.updateIDList), self.expected))

	def record_comparison(self, testcase, expected):
		if len(testcase) != len(expected): return False 
		for y in range(len(testcase)):
			if (testcase[y].timestamp != expected[y].timestamp) and (testcase[y].txid != expected[y].txid) and (testcase[y].updateid != expected[y].updateid): return False
		return True


class TestPageRank(unittest.TestCase):
	def setUp(self):
		self.testcaseGraph = nx.DiGraph()
		self.testcaseGraph.add_edge("A", "B")
		self.testcaseGraph.add_edge("A", "C")
		self.testcaseGraph.add_edge("C", "A")
		self.testcaseGraph.add_edge("B", "D")
		self.testcaseGraph.add_edge("C", "B")
		self.testcaseGraph.add_edge("D", "C")
		self.testcaseGraph.add_edge("C", "D")
		self.expected = {"A": 0.13867252, "B": 0.19760835, "C": 0.35707951, "D": 0.30663962}

	def test_pagerank(self):
		PR = TI.PageRank(self.testcaseGraph)
		self.assertTrue(self.rank_comparison(PR, self.expected))

	def rank_comparison(self, testList, expectedList):
		return set(testList) == set(expectedList)

class TestAntiTrustRank(unittest.TestCase):
	def setUp(self):
		self.testcaseGraph = nx.DiGraph()
		self.testcaseGraph.add_edge("A", "B")
		self.testcaseGraph.add_edge("A", "C")
		self.testcaseGraph.add_edge("C", "A")
		self.testcaseGraph.add_edge("B", "D")
		self.testcaseGraph.add_edge("C", "B")
		self.testcaseGraph.add_edge("D", "C")
		self.testcaseGraph.add_edge("C", "D")
		self.testcaseSeedSet = ["D"]
		self.expected = {'A': 0.55, 'B': 2.9000000000000004, 'C': 2.9, 'D': 1.1}

	def test_atr(self):
		ATR = TI.AntiTrustRank(self.testcaseGraph, self.testcaseSeedSet)
		self.assertTrue(self.rank_comparison(ATR, self.expected))

	def rank_comparison(self, testList, expectedList):
		return set(testList) == set(expectedList)
