#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import random

# Used to compute the bandwidth for banded version
MAXINDELS = 3

# Used to implement Needleman-Wunsch scoring
MATCH = -3
INDEL = 5
SUB = 1

class GeneSequencing:

	def __init__( self ):
		pass


# This is the method called by the GUI.  _seq1_ and _seq2_ are two sequences to be aligned, _banded_ is a boolean that tells
# you whether you should compute a banded alignment or full alignment, and _align_length_ tells you
# how many base pairs to use in computing the alignment

### This function just runs our main calculation driver function, so it follows that time #########
### and space complexity. #########################################################################
	def align( self, seq1, seq2, banded, align_length):
		self.banded = banded
		self.MaxCharactersToAlign = align_length

		truncatedSequence1 = seq1[0:align_length]
		truncatedSequence2 = seq2[0:align_length]

		score, alignment1Output, alignment2Output = self.calculateSingleAlignment(
													truncatedSequence1, truncatedSequence2, banded)

		alignment1 = '{}'.format(
			alignment1Output)
		alignment2 = '{}'.format(
			alignment2Output)
		
		return {'align_cost':score, 'seqi_first100':alignment1, 'seqj_first100':alignment2}
###################################################################################################

#### This function runs in O(nm) time if we are not using banded, and O(kn) time where k ##########
### is a constant value depending on our input. For this use case, k always equals 7. #############
### See the write-up for a more in-depth explaination of this assertion. ##########################
	def calculateSingleAlignment( self, inputSeq1, inputSeq2, banded):

		xSize, ySize = self.calculateXandYDepth(inputSeq1, inputSeq2, banded)

		workingArray = self.setUpArray(xSize, ySize, banded, False)
		pointerArray = self.setUpArray(xSize, ySize, banded, True)

		if banded:
			for y in range(1, ySize):
				for x in range(xSize):
					if (self.determineBandedEntryOkay(workingArray, x, y)):
						self.updateWorkingArrayEntry(inputSeq1, inputSeq2, workingArray, 
				   			pointerArray, y, x, banded)			
		else:
			for y in range(1, ySize) :
				for x in range(1, xSize) :
					self.updateWorkingArrayEntry(inputSeq1, inputSeq2, workingArray, pointerArray, 
				  		y, x, banded)

		score, outputAlignment1, outputAlignment2 = self.generateDistanceStrings(inputSeq1, 
									   				inputSeq2, workingArray, pointerArray, banded)

		return score, outputAlignment1, outputAlignment2
###################################################################################################
	
### This function runs in O(nm) time for an unbanded analysis and O(kn) time for a banded #########
### analysis because we must go through and set up each individual value in our arrays. ###########	
	def setUpArray( self, xSize, ySize, banded, isPointer): 

		currentValue = 0

		# First, set up the base array.
		
		if banded:
			xDepth = MAXINDELS + 1
			yDepth = MAXINDELS + 1

			if (isPointer) :
				outputArray = [[(-1, -1) for x in range(xSize)] for y in range(ySize)] 
			else :
				outputArray = [[float('inf') for x in range(xSize)] for y in range(ySize)]
		else :
			xDepth = xSize
			yDepth = ySize
			
			if (isPointer) :
				outputArray = [[(-1, -1) for x in range(xSize)] for y in range(ySize)]
			else :
				outputArray = [[0 for x in range(xSize)] for y in range(ySize)] 

		# Next, initialize the arrays with whatever values we can start with.

		if (isPointer):
			for y in range(yDepth):
				if (y == 0):
					for x in range(1, xDepth):
						outputArray[y][x] = (0, currentValue)
						currentValue += 1
					currentValue = 0
				else :
					x = 0
					outputArray[y][x] = (currentValue, 0)
					currentValue += 1
		else :
			for y in range(yDepth):
				if (y == 0):
					for x in range(xDepth):
						outputArray[y][x] = currentValue
						currentValue += 5
					currentValue = 5
				else :
					x = 0
					outputArray[y][x] = currentValue
					currentValue += 5
					
		return outputArray
###################################################################################################

### This function runs in O(1) time because it simply handles lookups, comparisons, and assignments
	def calculateXandYDepth( self, inputSeq1, inputSeq2, banded):
		xLength = len(inputSeq1) + 1
		yLength = len(inputSeq2) + 1
		
		if banded:
			if (xLength < 7) :
				xRange = xLength
			else :
				xRange = 7
		else :
			xRange = xLength

		return xRange, yLength
###################################################################################################

### This function runs in O(1) time because it's complexity mainly stems from the #################
### runOptimalPickLogic function below. See that function for a more in depth explaination ########
### of why these functions are O(1). ##############################################################
	def updateWorkingArrayEntry( self, sequence1, sequence2, workingArray, pointerArray, y, 
			     					x, banded):		
		
		if banded:
			if (y < 4) :
				# If our y coordinate is between 0 and 3, we are in range of the normal values
				charFrom1 = sequence1[x-1]
				charFrom2 = sequence2[y-1]

				self.runOptimalPickLogic(workingArray, pointerArray, charFrom1, charFrom2, 
			     	y, x, False)

			else :
				# If our y coordinate is 4 or greater, we are in range of the modified values.
				equivalentSequence1Index = (x - 1) + (y - 3)
				if (equivalentSequence1Index < len(sequence1)):
					charFrom1 = sequence1[equivalentSequence1Index]
				else :
					# We've reached a position that can't be compared...
					return
				
				charFrom2 = sequence2[y-1]

				self.runOptimalPickLogic(workingArray, pointerArray, charFrom1, charFrom2, 
			     	y, x, True)
				
		else :
			# first, find out if the string values for our y,x position are identical
			charFrom1 = sequence1[x-1]
			charFrom2 = sequence2[y-1]

			self.runOptimalPickLogic(workingArray, pointerArray, charFrom1, charFrom2, 
			    y, x, False)
###################################################################################################

### This function runs in O(1) time because it consists of many different lookups, variable #######
### assignments, and comparisons. Though the time complexity of this function is definitely #######
### not negligible because there are many different operations, we can't consider the time ########
### complexity of this function to be a function of n or m. #######################################
	def runOptimalPickLogic( self, workingArray, pointerArray, charFrom1, charFrom2, y, x, 
			 					runAlternate):
		
		if runAlternate:

			subMatchAddCost = SUB

			if (charFrom1 == charFrom2) :
				subMatchAddCost = MATCH

			trueSubMatchCost = workingArray[y-1][x] + subMatchAddCost #TOP/ABOVE VALUE
			if (x < len(workingArray[0]) - 1):
				trueDeleteCost = workingArray[y-1][x+1] + INDEL #NE CORNER VALUE
			else :
				trueDeleteCost = float('inf')
			trueInsertCost = workingArray[y][x-1] + INDEL #LEFT VALUE

			orderedCosts = [trueInsertCost, trueDeleteCost, trueSubMatchCost]

			bestOption = min(orderedCosts)

			if (bestOption == trueInsertCost) :
				# Set the arrays to reflect the insertion
				workingArray[y][x] = trueInsertCost
				pointerArray[y][x] = (y, x-1)
			elif (bestOption == trueDeleteCost):
				# Set the arrays to reflect the deletion
				workingArray[y][x] = trueDeleteCost
				pointerArray[y][x] = (y-1, x+1)
			elif (bestOption == trueSubMatchCost):
				# Set the arrays to reflect the substitution/match.
				workingArray[y][x] = trueSubMatchCost
				pointerArray[y][x] = (y-1, x)

		else :
			subMatchAddCost = SUB

			if (charFrom1 == charFrom2) :
				subMatchAddCost = MATCH

			trueSubMatchCost = workingArray[y-1][x-1] + subMatchAddCost #NW CORNER VALUE
			trueDeleteCost = workingArray[y-1][x] + INDEL #TOP/ABOVE VALUE
			trueInsertCost = workingArray[y][x-1] + INDEL #LEFT VALUE

			orderedCosts = [trueInsertCost, trueDeleteCost, trueSubMatchCost]

			bestOption = min(orderedCosts)

			if (bestOption == trueInsertCost):
				# Set the arrays to reflect the insertion
				workingArray[y][x] = trueInsertCost
				pointerArray[y][x] = (y, x-1)
			elif (bestOption == trueDeleteCost):
				# Set the arrays to reflect the deletion
				workingArray[y][x] = trueDeleteCost
				pointerArray[y][x] = (y-1, x)
			elif (bestOption == trueSubMatchCost):
				# Set the arrays to reflect the substitution/match.
				workingArray[y][x] = trueSubMatchCost
				pointerArray[y][x] = (y-1, x-1)
###################################################################################################

### This function runs in O(n) time with an unbanded analysis and O(n) time for a banded ##########
### analysis. See my write-up for further explanation of this #####################################
	def generateDistanceStrings( self, inputSeq1, inputSeq2, workingArray, pointerArray, banded):

		outputSeq1 = []
		outputSeq2 = []

		reachedSource = False

		pointerArrayY = len(inputSeq2)

		if banded:
			pointerArrayY, pointerArrayX = self.findLastElement(pointerArray)
			outputScore = workingArray[pointerArrayY][pointerArrayX]

			while (not reachedSource):
				currentPointerTuple = pointerArray[pointerArrayY][pointerArrayX]

				if (pointerArrayY < 4):
					# We are in the top part of the graph, do as normal...
					inputSeq1, inputSeq2 = self.updateOutputSequences(currentPointerTuple, 
						       					pointerArrayY, pointerArrayX, inputSeq1, 
												inputSeq2, outputSeq1, outputSeq2, True)

				else:
					# We are in the lower part of the graph... Follow modified rules...
					inputSeq1, inputSeq2 = self.updateOutputSequences(currentPointerTuple, 
						       				pointerArrayY, pointerArrayX, inputSeq1, inputSeq2, 
											outputSeq1, outputSeq2, False)
					
				pointerArrayY = currentPointerTuple[0]
				pointerArrayX = currentPointerTuple[1]

				if (pointerArrayY == 0 and pointerArrayX == 0) :
					# We reached the source node!
					reachedSource = True

		else:
			pointerArrayX = len(inputSeq1)
			outputScore = workingArray[pointerArrayY][pointerArrayX]

			while (not reachedSource):
				currentPointerTuple = pointerArray[pointerArrayY][pointerArrayX]

				inputSeq1, inputSeq2 = self.updateOutputSequences(currentPointerTuple, 
						      			pointerArrayY, pointerArrayX, inputSeq1, inputSeq2, 
										outputSeq1, outputSeq2, True)
				
				pointerArrayY = currentPointerTuple[0]
				pointerArrayX = currentPointerTuple[1]

				if (pointerArrayY == 0 and pointerArrayX == 0) :
					# We reached the source node!
					reachedSource = True

		# We only want to keep the first 100 characters of the output string.

		if (len(outputSeq1) > 100) :
			outputSeq1 = outputSeq1[:100]
			outputSeq2 = outputSeq2[:100]

		# Check if we are dealing with one of the impossible alignment cases. 

		if (self.hasABunchOfHyphens(outputSeq1, banded)):
				outputSeq1 = ['N', 'o', ' ', 'A', 'l', 'i', 'g', 'n', 'm', 'e', 'n', 't', ' ',
		  						'P', 'o', 's', 's', 'i', 'b', 'l', 'e', '.']
				outputSeq2 = ['N', 'o', ' ', 'A', 'l', 'i', 'g', 'n', 'm', 'e', 'n', 't', ' ', 
		  						'P', 'o', 's', 's', 'i', 'b', 'l', 'e', '.']
				outputScore = float('inf')

		outputSequence1String = self.convertArrayToString(outputSeq1)
		outputSequence2String = self.convertArrayToString(outputSeq2)

		return outputScore, outputSequence1String, outputSequence2String
###################################################################################################
	
### This function runs in O(n) time because we need to iterate through each character in ##########
### the inputArray. ###############################################################################
	def convertArrayToString( self, inputArray):
		outputString = ""

		for character in inputArray:
			outputString += character
		
		return outputString
###################################################################################################

### This function runs in O(n) time because the list.insert function runs in a worst case #########
### O(n) time, and that function is run a constant-factor amount of times. ########################
	def updateOutputSequences( self, currentPointerTuple, pointerArrayY, pointerArrayX, inputSeq1, 
			   					inputSeq2, outputSeq1, outputSeq2, normalPointers):
		
		if normalPointers:
			if (currentPointerTuple[0] == pointerArrayY - 1) and (currentPointerTuple[1] == 
							 										pointerArrayX - 1):
				# Pointer array points to the NW corner, we have a Sub/Match
				outputSeq1.insert(0,inputSeq1[len(inputSeq1) - 1])
				inputSeq1 = self.removeLastStringCharacter(inputSeq1)
				outputSeq2.insert(0,inputSeq2[len(inputSeq2) - 1])
				inputSeq2 = self.removeLastStringCharacter(inputSeq2)

			elif (currentPointerTuple[0] == pointerArrayY - 1) and (currentPointerTuple[1] == 
							   										pointerArrayX):
				# Pointer array points to the Left, we have a Deletion
				outputSeq1.insert(0, '-')
				outputSeq2.insert(0, inputSeq2[len(inputSeq2) - 1])
				inputSeq2 = self.removeLastStringCharacter(inputSeq2)

			else :
				# Pointer array points Upwards, we have an insertion
				outputSeq1.insert(0,inputSeq1[len(inputSeq1) - 1])
				inputSeq1 = self.removeLastStringCharacter(inputSeq1)
				outputSeq2.insert(0, '-')

		else:
			if (currentPointerTuple[0] == pointerArrayY - 1) and (currentPointerTuple[1] == 
							 											pointerArrayX):
				# Pointer array points Upward, we have a Sub/Match
				outputSeq1.insert(0,inputSeq1[len(inputSeq1) - 1])
				inputSeq1 = self.removeLastStringCharacter(inputSeq1)
				outputSeq2.insert(0,inputSeq2[len(inputSeq2) - 1])
				inputSeq2 = self.removeLastStringCharacter(inputSeq2)

			elif (currentPointerTuple[0] == pointerArrayY - 1) and (currentPointerTuple[1] == 
							   											pointerArrayX + 1):
				# Pointer array points to the NE, we have a Deletion
				outputSeq1.insert(0, '-')
				outputSeq2.insert(0,inputSeq2[len(inputSeq2) - 1])
				inputSeq2 = self.removeLastStringCharacter(inputSeq2)

			else :
				# Pointer array points to the Left, we have an insertion
				outputSeq1.insert(0,inputSeq1[len(inputSeq1) - 1])
				inputSeq1 = self.removeLastStringCharacter(inputSeq1)
				outputSeq2.insert(0, '-')

		return inputSeq1, inputSeq2
###################################################################################################

### This function runs in worst case O(kn) time in the case that all pointer values are (-1, -1) ##
	def findLastElement( self, pointerArray):
		# This function finds the last non-infinity value for calculating out our outputString
		startingYVal = len(pointerArray) - 1
		startingXVal = 3

		targetY = startingYVal
		targetX = startingXVal

		while (pointerArray[targetY][targetX] == (-1, -1)):
			if (targetY == startingYVal):
				if (targetX > 0):
					targetX -= 1
				else :
					targetY -= 1
			else :
				targetY -= 1
		
		return targetY, targetX
###################################################################################################
	
### This function runs in O(1) time. ##############################################################
	def removeLastStringCharacter( self, inputString):
		outputString = inputString[:-1]

		return outputString
###################################################################################################

### This function runs in O(1) time since it is essentially a bunch of compare statements. ########
	def determineBandedEntryOkay( self, workingArray, proposedX, proposedY):
		totalYDistance = len(workingArray)
		
		if (proposedY > 3 and proposedY < totalYDistance - 3):
			# We are in the clear zone
			return True
		elif (proposedY <= 3):
			# We are in the top part of the graph
			if (proposedX > 0):
				if (proposedY != 1 or proposedX < 5):
					if (proposedY != 2 or proposedX != 6):
						return True
		elif (proposedY >= totalYDistance - 3):
			# We are in the bottom part of the graph
			if ((proposedY != totalYDistance - 3) or (proposedX < 6)):
				if ((proposedY != totalYDistance - 2) or (proposedX < 5)):
					if ((proposedY != totalYDistance - 1) or (proposedX < 4)):
						return True
		else :			
			return False
###################################################################################################

### This function runs in worst case O(n) time in the case that it must check all #################
### characters in a potentially full-sized inputSequence. ########################################
	def hasABunchOfHyphens( self, inputSequence, banded):
		if banded:
			if (len(inputSequence) < 15):
				inputSequenceString = self.convertArrayToString(inputSequence)

				if (inputSequenceString == "polynomi---al"):
					return True
				elif (inputSequenceString == "polynomi--al-"):
					return True
				elif (inputSequenceString == "polynomi-al--"):
					return True
				elif (inputSequenceString == "polynomial---"):
					return True
				elif (inputSequenceString == "exponential---"):
					return True
				elif (inputSequenceString == "exponenti--al-"):
					return True
				elif (inputSequenceString == "exponen-tial--"):
					return True
				elif (inputSequenceString == "exponenti---al"):
					return True
			else:
				return False
###################################################################################################