import numpy as np
import random

class MarkovChain:
	def __init__(self, fileName):
		file = open(fileName, "r")

		self.rows = int(file.readline())
		self.columns = int(file.readline())

		self.seq_to_index_i = {}
		self.index_i_to_seq = {}
		self.start_seq_count = {}
		for i in range(self.rows):
			line = file.readline().split()
			seq = line[0] + " " + line[1]
			self.seq_to_index_i[seq] = i
			self.index_i_to_seq[i] = seq
			if (line[2] == "1"):
				if (seq in self.start_seq_count.keys()):
					self.start_seq_count[seq] += 1
				else:
					self.start_seq_count[seq] = 1
				

		self.index_j_to_token = {}	
		self.token_to_index_j = {}
		for j in range(self.columns):
			line = file.readline().rstrip('\n')
			self.token_to_index_j[line] = j
			self.index_j_to_token[j] = line

		self.matrix = np.zeros((self.rows, self.columns))
		for i in range(self.rows):
			line = file.readline()
			data = line.split()
			for j in range(self.columns):
				self.matrix[i][j] = data[j]

		self.messageCount = int(file.readline())

		file.close()

	def printMatrix(self):
		print(self.matrix)

	def incrementMessageCount(self):
		self.messageCount += 1

	def getMessageCount(self):
		return self.messageCount

	def updateModel(self, line):
		data = line.split()
		data.append("")
		for i in range(len(data) - 2):
			seq = data[i] + " " + data[i + 1]
			if (i == 0):
				if (seq in self.start_seq_count.keys()):
					self.start_seq_count[seq] += 1
				else:
					self.start_seq_count[seq] = 1
			if (seq in self.seq_to_index_i.keys()):
				token = data[i + 2]
				if (token in self.token_to_index_j.keys()):
					self.matrix[self.seq_to_index_i[seq]][self.token_to_index_j[token]] += 1
				else:
					newCol = np.zeros((self.rows, 1))
					newCol[self.seq_to_index_i[seq]] += 1
					self.matrix = np.hstack((self.matrix, newCol))
					self.token_to_index_j[token] = self.columns
					self.index_j_to_token[self.columns] = token
					self.columns += 1
			else:
				newRow = np.zeros((1, self.columns))
				self.matrix = np.vstack((self.matrix, newRow))
				self.seq_to_index_i[seq] = self.rows
				self.index_i_to_seq[self.rows] = seq
				self.rows += 1
				token = data[i + 2]
				if (token in self.token_to_index_j.keys()):
					self.matrix[self.seq_to_index_i[seq]][self.token_to_index_j[token]] += 1
				else:
					newCol = np.zeros((self.rows, 1))
					newCol[self.seq_to_index_i[seq]] += 1
					self.matrix = np.hstack((self.matrix, newCol))
					self.token_to_index_j[token] = self.columns
					self.index_j_to_token[self.columns] = token
					self.columns += 1


	def saveToFile(self, fileName):
		file = open(fileName, "w")

		file.write(str(self.rows) + "\n")
		file.write(str(self.columns) + "\n")

		for i in range(self.rows):
			file.write(self.index_i_to_seq[i])
			if (self.index_i_to_seq[i] in self.start_seq_count.keys()):
				file.write(" " + str(1) + "\n")
			else: file.write(" " + str(0) + "\n")

		for j in range(self.columns):
			file.write(self.index_j_to_token[j] + "\n")

		for i in range(self.rows):
			for j in range(self.columns):
				file.write(str(self.matrix[i][j]) + " ")
			file.write("\n")

		file.write(str(self.messageCount))

		file.close()

	def getProbabilitiesFromOccurences(self, v):
		total = 0.0
		for i in range(self.columns):
			total += v[i]
		return v / total

	def obtainStart(self):
		total = 0.0
		sequences = []
		probabilities = []
		for key in self.start_seq_count.keys():
			total += self.start_seq_count[key]
		for key in self.start_seq_count.keys():
			sequences.append(key)
			probabilities.append(self.start_seq_count[key] / total)
		result = np.random.choice(sequences, 1, p=probabilities)
		for string in result:
			return string.split()
		

	def sampleNextToken(self, seq, alpha):
		if (seq in self.seq_to_index_i.keys()):
			i = self.seq_to_index_i[seq]
			probabilities = MarkovChain.getProbabilitiesFromOccurences(self, self.matrix[i])
			j = np.random.choice(self.columns, 1, p=probabilities)
			return self.index_j_to_token[j[0]]
		else:
			p = random.uniform(0, 1)
			if (p > alpha):
				return ""
			else:
				j = np.random.choice(self.columns, 1)
				return self.index_j_to_token[j[0]]

	def constructSequence(self, length):
		sequence = MarkovChain.obtainStart(self)
		#print(sequence)

		while (len(sequence) <= length and sequence[len(sequence) - 1] != ""):
			sequence.append(MarkovChain.sampleNextToken(self, sequence[len(sequence) - 2] + " " + sequence[len(sequence) - 1], 0.1))

		result = ""
		for i in range(len(sequence)):
			result += sequence[i] + " "
		return result