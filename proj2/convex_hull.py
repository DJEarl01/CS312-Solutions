from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseHull(self,polygon):
		self.view.clearLines(polygon)

	def showText(self,text):
		self.view.displayStatusText(text)

# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()

		# Sort the input points by X-Value. This runs in O(nlogn) time and O(n) space.
		# COMMENT - the sort method runs in nlogn time, the key runs in constant time. The sort method sorts in place, so the space is O(n).
		sortedPoints = []
		for i in points:
			sortedPoints.append(i) # The input points are copied, but that only increases space by a constant factor.

		def sortByXVal(point):
			return point.x()

		sortedPoints.sort(key=sortByXVal)

		t2 = time.time()

		# My recursive divide and conquer function is below --------------------------------
		# It runs in O(nlogn) time and O(n) space. 

		def divAndConquerConvex_Hull(inputPointsLeft, inputPointsRight): #input is two point lists, one for each previously generated hull.

			# Start everything out by checking for our base case and handling our recursion. This splits the problem in two equal pieces, 
				# so our a and b values are 2
			# This corresponds to MARKER 1 - DIVIDING INTO TWO SMALLER HULLS
			
			# We start by handling the right side hull.
			if (len(inputPointsLeft) > 3):
				currentPointsLeft = divAndConquerConvex_Hull([inputPointsLeft[i] for i in range(len(inputPointsLeft)//2)], 
						 [inputPointsLeft[i+(len(inputPointsLeft)//2)] for i in range((len(inputPointsLeft)//2) + len(inputPointsLeft)%2)])
			else:
				currentPointsLeft = inputPointsLeft

			# We continue by handling the left side hull.
			if (len(inputPointsRight) > 3):
				currentPointsRight = divAndConquerConvex_Hull([inputPointsRight[i] for i in range(len(inputPointsRight)//2)], 
						  [inputPointsRight[i+(len(inputPointsRight)//2)] for i in range((len(inputPointsRight)//2) + len(inputPointsRight)%2)])
			else:
				currentPointsRight = inputPointsRight

			# At this point in the algorithm, we have the two smallest polygons at our disposal...
			# Now, we run the tangent connector part of the algorithm (merge)

			# This corresponds to MARKER 2 - INITIAL SORT BY CLOCKWISE/COUNTER-CLOCKWISE POSITION

			# Make a sorted list of points in the right polygon based on clockwise order from the leftmost point
				# Sort by making a key function that calculates the slope between point one and the target point.

			currentPointsRight.sort(key=sortByXVal) # This runs in nlogn time and n space

			baseCurrentPointsRight = currentPointsRight.copy()

			def rightPolygonPointSortKey(point): # This calculation runs in constant time... It's just a calculation
				if (point.x() == baseCurrentPointsRight[len(currentPointsRight)-1].x()):
					slope = float('-inf')
				else: 
					slope = (point.y() - baseCurrentPointsRight[len(currentPointsRight)-1].y()) / (point.x() - 
										    baseCurrentPointsRight[len(currentPointsRight)-1].x())
				return slope
			
			currentPointsRight.sort(key=rightPolygonPointSortKey)
			
			# Make a sorted list of points in the left polygon based on counter-clockwise order from the rightmost point
				# Sort by making a key function that calculates the slope between point one and the target point.

			currentPointsLeft.sort(key=sortByXVal) # Same deal here... nlogn time, n space. 

			baseCurrentPointsLeft = currentPointsLeft.copy()

			def leftPolygonPointSortKey(point): # Also just constant time
				if (point.x() == baseCurrentPointsLeft[0].x()):
					slope = float('inf')
				else: 
					slope = (point.y() - baseCurrentPointsLeft[0].y()) / (point.x() - baseCurrentPointsLeft[0].x())
				return -1*slope
			
			currentPointsLeft.sort(key=leftPolygonPointSortKey)

			# -------- FINDING THE TOP TANGENT POINTS ---------
			# First we find the rightmost point in the left hull and the leftmost point in the right hull
			# This corresponds to MARKER 3 - CALCULATE INNER POINTS

			rightmostLeftHullPoint = 0
			for currentLeftPoint in range(len(currentPointsLeft)): # This part runs through all of the current points once and classifies them, 
																      # running in n time and n space
				if (currentPointsLeft[currentLeftPoint].x() > currentPointsLeft[rightmostLeftHullPoint].x()):
					rightmostLeftHullPoint = currentLeftPoint
			leftmostRightHullPoint = 0
			for currentRightPoint in range(len(currentPointsRight)): # This also runs in n time and n space
				if (currentPointsRight[currentRightPoint].x() < currentPointsRight[leftmostRightHullPoint].x()):
					leftmostRightHullPoint = currentRightPoint

			targetLeftPointIndex = rightmostLeftHullPoint
			targetRightPointIndex = leftmostRightHullPoint

			# This corresponds to MARKER 4 - TOP TANGENT FINDER

			# Make a main while loop that checks if both left and right up moves happened in the current cycle
			# This loop runs in O(n) time and O(n) space, because at most it just iterates through all points calculating a constant time 
				# comparison between all of them once.
			madeNewTopConnection = True
			while (madeNewTopConnection == True): # while a new connection is made between one of the left or right while loops
				madeNewTopConnection = False
				# Get the current Slope that we have between our target tangent points to use for comparison
				acceptedSlope = (currentPointsLeft[targetLeftPointIndex].y() - 
		     		currentPointsRight[targetRightPointIndex].y()) / (currentPointsLeft[targetLeftPointIndex].x() - 
						currentPointsRight[targetRightPointIndex].x())

				# Make a left side while loop that runs until moving the target point counter-clockwise (bacwards in our sorted list) 
					# makes the total slope increase
				tempTargetIndex = (targetLeftPointIndex-1) % len(currentPointsLeft)
				testSlope = (currentPointsLeft[tempTargetIndex].y() - 
		 			currentPointsRight[targetRightPointIndex].y())/(currentPointsLeft[tempTargetIndex].x() - 
						currentPointsRight[targetRightPointIndex].x())
				movedCCWOne = False

				# This while loop is treated as an if statement for the above logic. If the if returns true, keep running that logic.
				while (testSlope < acceptedSlope):
					movedCCWOne = True	# Tell the overall while loop to run more time
					acceptedSlope = testSlope # Set the new slope to be our accepted slope because it is determined to be better.
					targetLeftPointIndex = tempTargetIndex # Set the target tangent point to our current point index

					tempTargetIndex = (tempTargetIndex - 1) % len(currentPointsLeft) # Move one index clockwise
					if (tempTargetIndex == targetLeftPointIndex): # Precautionary Stop in case we make it all the way around the hull
						break
					testSlope = (currentPointsLeft[tempTargetIndex].y() - 
		  				currentPointsRight[targetRightPointIndex].y())/(currentPointsLeft[tempTargetIndex].x() - 
							currentPointsRight[targetRightPointIndex].x())

				if (movedCCWOne):
					madeNewTopConnection = True

				# Make a right side while loop that runs until moving the target point clockwise (backwards in our sorted list) makes the 
					# total slope decrease
				movedCWOne = False
				tempTargetIndex = (targetRightPointIndex - 1) % len(currentPointsRight)
				testSlope = (currentPointsLeft[targetLeftPointIndex].y() - 
		 			currentPointsRight[tempTargetIndex].y())/(currentPointsLeft[targetLeftPointIndex].x() - 
						currentPointsRight[tempTargetIndex].x())
				
				# Run the above loop just flipped for testing the right side hull.
				while (testSlope > acceptedSlope):
					movedCWOne = True	# Tell the main while loop to run again
					acceptedSlope = testSlope # Set the input slope to be our accepted slope
					targetRightPointIndex = tempTargetIndex # Set the target tangent point to our current point index

					tempTargetIndex = (tempTargetIndex - 1) % len(currentPointsRight) # Move one index clockwise
					if (tempTargetIndex == targetRightPointIndex):
						break
					testSlope = (currentPointsLeft[targetLeftPointIndex].y() - 
		  				currentPointsRight[tempTargetIndex].y())/(currentPointsLeft[targetLeftPointIndex].x() - 
							currentPointsRight[tempTargetIndex].x())

				if (movedCWOne):
					madeNewTopConnection = True
			
			topTangent = [currentPointsLeft[targetLeftPointIndex], currentPointsRight[targetRightPointIndex]]
					
			# -------- FINDING THE BOTTOM TANGENT POINTS ---------
			# Make the above algorithm but flipped to run for the bottom tangent.

			# This corresponds to MARKER 5 - BOTTOM TANGENT FINDER

			# Set our starting target values...
			targetLeftPointIndex = rightmostLeftHullPoint
			targetRightPointIndex = leftmostRightHullPoint
			madeNewTopConnection = True
			while (madeNewTopConnection == True): # while a new connection is made between one of the left or right while loops
				madeNewTopConnection = False
				acceptedSlope = (currentPointsLeft[targetLeftPointIndex].y() - 
		     		currentPointsRight[targetRightPointIndex].y())/(currentPointsLeft[targetLeftPointIndex].x() - 
						currentPointsRight[targetRightPointIndex].x())
				
				# Make a left side while loop that runs until moving the target point counter-clockwise (bacwards in our sorted list) makes 
					# the total slope increase
				movedCWOne = False
				tempTargetIndex = (targetLeftPointIndex+1) % len(currentPointsLeft)
				testSlope = (currentPointsLeft[tempTargetIndex].y() - 
		 			currentPointsRight[targetRightPointIndex].y())/(currentPointsLeft[tempTargetIndex].x() - 
						currentPointsRight[targetRightPointIndex].x())
				
				while (testSlope > acceptedSlope):
					movedCWOne = True	# Allow the while loop to run more
					acceptedSlope = testSlope # Set the new slope to be our accepted slope
					targetLeftPointIndex = tempTargetIndex # Set the target tangent point to our current point index

					tempTargetIndex = (tempTargetIndex + 1) % len(currentPointsLeft) # Move one index clockwise
					if (tempTargetIndex == targetLeftPointIndex):
						break
					testSlope = (currentPointsLeft[tempTargetIndex].y() - 
		  				currentPointsRight[targetRightPointIndex].y())/(currentPointsLeft[tempTargetIndex].x() - 
							currentPointsRight[targetRightPointIndex].x())

				if (movedCWOne):
					madeNewTopConnection = True

				# Make a right side while loop that runs until moving the target point clockwise (backwards in our sorted list) makes the 
					# total slope decrease
				movedCCWOne = False
				tempTargetIndex = (targetRightPointIndex+1) % len(currentPointsRight)
				testSlope = (currentPointsLeft[targetLeftPointIndex].y() - 
		 			currentPointsRight[tempTargetIndex].y())/(currentPointsLeft[targetLeftPointIndex].x() - 
						currentPointsRight[tempTargetIndex].x())
				
				while (testSlope < acceptedSlope):
					movedCCWOne = True	# Allow the while loop to run more
					acceptedSlope = testSlope # Set the new slope to be our accepted slope
					targetRightPointIndex = tempTargetIndex # Set the target tangent point to our current point index

					tempTargetIndex = (tempTargetIndex + 1) % len(currentPointsRight) # Move one index clockwise
					if (tempTargetIndex == targetRightPointIndex):
						break
					testSlope = (currentPointsLeft[targetLeftPointIndex].y() - 
		  				currentPointsRight[tempTargetIndex].y())/(currentPointsLeft[targetLeftPointIndex].x() - 
							currentPointsRight[tempTargetIndex].x())

				if (movedCCWOne):
					madeNewTopConnection = True
			
			bottomTangent = [currentPointsLeft[targetLeftPointIndex], currentPointsRight[targetRightPointIndex]]

			# Now that the tangent lines are done, we need to remove the points that are now interior from rightPolygon and leftPolygon lists.
			# Do this by starting at the top tangent point on the left hull and adding points ccw until you hit bottom tangent
				# and start at top tangent point on right hull and add points cw until you hit bottom tangent
			# This function piece runs in O(n) time and O(n) space because it runs through at most all of the points once.

			# This corresponds to MARKER 6 - REMOVE INTERIOR POINTS

			newCurrentPointsLeft = []
			# Traverse each point counter clockwise starting at the top tangent point and ending at the bottom tangent point
			topTangentAnchorPointIndex = currentPointsLeft.index(topTangent[0])
			bottomTangentAnchorPointIndex = currentPointsLeft.index(bottomTangent[0])
			if (bottomTangentAnchorPointIndex > topTangentAnchorPointIndex): # There is a case where the top tangent is numerically higher in 
																				# the sorted point list than the bottom. If this is the case, 
																				# flip the index using modulus.
				bottomTangentAnchorPointIndex -= len(currentPointsLeft)
			for targetPointIndex in range(topTangentAnchorPointIndex, bottomTangentAnchorPointIndex-1, -1):
				if (targetPointIndex < 0):
					adjustedIndex = len(currentPointsLeft) + targetPointIndex
				else:
					adjustedIndex = targetPointIndex
				newCurrentPointsLeft.append(currentPointsLeft[adjustedIndex])
			
			newCurrentPointsRight = []
			# Traverse each point clockwise starting at the top tangent point and ending at the bottom tangent point
			topTangentAnchorPointIndex = currentPointsRight.index(topTangent[1])
			bottomTangentAnchorPointIndex = currentPointsRight.index(bottomTangent[1])
			if (bottomTangentAnchorPointIndex > topTangentAnchorPointIndex):
				bottomTangentAnchorPointIndex -= len(currentPointsRight)
			for targetPointIndex in range(topTangentAnchorPointIndex, bottomTangentAnchorPointIndex-1, -1):
				if (targetPointIndex < 0):
					adjustedIndex = len(currentPointsRight) + targetPointIndex
				else:
					adjustedIndex = targetPointIndex
				newCurrentPointsRight.append(currentPointsRight[adjustedIndex])

			# Each point in the hull should now be present in newCurrentPointsLeft and newCurrentPointsRight
			totalPolygon = newCurrentPointsLeft + newCurrentPointsRight

			if (False): # Simple toggle for the blink function to visualize the recursion
				pointsInHull = totalPolygon.copy()
				pointsInHull.sort(key=sortByXVal)

				baseCurrentPoints = pointsInHull.copy()

				def hullPolygonPointSortKey(point):
					if (point.x() == baseCurrentPoints[0].x()):
						slope = float('-inf')
					else: 
						slope = (point.y() - baseCurrentPoints[0].y()) / (point.x() - baseCurrentPoints[0].x())
					return slope
			
				pointsInHull.sort(key=hullPolygonPointSortKey)
				self.blinkTangent([QLineF(pointsInHull[i], pointsInHull[(i+1)%len(pointsInHull)]) for i in range(len(pointsInHull))], RED)

			return totalPolygon

		t3 = time.time()

		# This is the starter to my recursive solver function... It feeds the original case of splitting the sortedPoints into 2 somewhat 
		# even groups

		pointsInHull = divAndConquerConvex_Hull([sortedPoints[i] for i in range(len(sortedPoints)//2)], 
					  [sortedPoints[i+(len(sortedPoints)//2)] for i in range((len(sortedPoints)//2) + len(sortedPoints)%2)])

		# We now have all of the points in the hull, so we need to turn them into a polygon with QLineF. 
		# All of these points can come out unsorted, so I use the algorithm to sort them by clockwise order.

		pointsInHull.sort(key=sortByXVal)

		baseCurrentPoints = pointsInHull.copy()

		def hullPolygonPointSortKey(point):
			if (point.x() == baseCurrentPoints[0].x()):
				slope = float('-inf')
			else: 
				slope = (point.y() - baseCurrentPoints[0].y()) / (point.x() - baseCurrentPoints[0].x())
			return slope
			
		pointsInHull.sort(key=hullPolygonPointSortKey)

		# Now that the points are sorted, make a simple polygon using a line between each of those points.

		polygon = [QLineF(pointsInHull[i], pointsInHull[(i+1)%len(pointsInHull)]) for i in range(len(pointsInHull))]

		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon,BLUE)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))