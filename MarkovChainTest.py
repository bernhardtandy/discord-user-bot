from MarkovChain import MarkovChain
import unittest

class TestMarkovChain(unittest.TestCase):

	def setUp(self):
		self.mc = MarkovChain("empty.txt")

	def test_empty(self):
		self.assertEqual(self.mc.printMatrix(), None)

	def test_updateModelSimple(self):
		self.mc.updateModel("Hello, my name is Andy!")

	#TODO
   	
if __name__ == '__main__':
    unittest.main()