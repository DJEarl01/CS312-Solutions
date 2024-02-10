#!/usr/bin/python3

from CS312Graph import *
import time


class NetworkRoutingSolver:
    def __init__( self):
        pass

    def initializeNetwork( self, network ):
        assert( type(network) == CS312Graph )
        self.network = network

    nodeDistances = [] # Array to keep track of distances between the source and all other nodes
    previousTracker = [] # Array to keep track of previous node pointers
    deletedIndexes = [] # Array to keep track of indexes that have been deleted from the priority queue
    
    def initializeDistanceArray(self, srcIndex): # Set up our distance array by walking through each Node
        self.nodeDistances.clear()
        for i in range(len(self.network.nodes)): 
            if (i == srcIndex):
                self.nodeDistances.append(0) # Our source node has a distance of 0 in our nodeDistances
            else:
                self.nodeDistances.append(float('inf'))

    def initializeTrackerArrays(self): # Set up our previous tracker and deleted indexes arrays
        self.previousTracker.clear()
        self.deletedIndexes.clear()
        for i in range(len(self.network.nodes)):
            self.previousTracker.append(None)
            self.deletedIndexes.append(0)

    # My Array Priority Queue implementation, which uses a dictionary for key-value pairs

    # The insert function below runs in O(1) time
    def insertToArray(self, inputArray, nodeIndex, nodeInitVal):
        inputArray[nodeIndex] = nodeInitVal

    # The decreaseKey function below runs in O(1) time
    def decreaseArrayItemKey(self, inputArray, index, newValue):
        if (index in inputArray):
            if (inputArray[index] > newValue):
                inputArray[index] = newValue
        else:
            inputArray[index] = newValue

    # The deleteMin function below runs in O(n) time
    def deleteMinInArray(self, inputArray):
        smallestValue = float('inf')
        smallestKey = -1

        for key in inputArray.keys(): # We run through all keys in our array to find the minimum
            if (self.deletedIndexes[key] == 0):
                if (inputArray[key] < smallestValue):
                    smallestValue = inputArray[key]
                    smallestKey = key

        inputArray.pop(smallestKey)
        self.deletedIndexes[smallestKey] = 1
        return smallestKey
    
    # This check function runs in O(1) time
    def arrayIsNotEmpty(self, inputArray):
        if (len(inputArray) != 0):
            return True
        else: 
            return False
    
    # My implementation of the Binary Heap Priority Queue

    def initializeHeap(self, inputHeap, inputPointerArray): # Set up our heap structure with the source node
        inputHeap.clear()
        inputPointerArray.clear()
        inputHeap[0] = 0
        inputPointerArray[0] = self.source

    # The bubbleUp function runs in O(logn) time. It takes in the working heap, pointer array, the index of the node we are manipulating in 
    #   the Network, the index it is currently at in the heap, and the value of the node we are manipulating.
    def bubbleUpBinaryHeap(self, inputHeap, inputPointerArray, nodeNetworkIndex, heapIndex, value):
        
        if (heapIndex == 0): # If the heapIndex we get is 0, we can't do any better because this node has no parents
            return 

        # Next we grab the parent heapIndex of our current Node
        if (heapIndex %2 == 1): #if our input index is odd, we need to do a simple floor divide
            parentIndex = heapIndex//2
        else: # if it is even, we need to subtract one from the floor divide in order to get the right parent index. 
            parentIndex = (heapIndex//2) - 1
        
        # Now that we have our parent index, we can compare the value of that index with the value of our current Node. 
        #   If the value of the parent is greater than our input value, then we bubble up.
        while (inputHeap[parentIndex] > value): # if the parent index has a bigger value than our new value, we need to bubble up. 
            previousParentItem = inputHeap[parentIndex]
            inputHeap[parentIndex] = inputHeap[heapIndex]
            inputHeap[heapIndex] = previousParentItem # This flips the values in the two places.

            previousParentNodeNetworkIndex = inputPointerArray[parentIndex]

            inputPointerArray[parentIndex] = nodeNetworkIndex
            inputPointerArray[heapIndex] = previousParentNodeNetworkIndex # This flips the nodes our pointer array. 

            # Now that we've bubbled up one time, we get the next parentIndex now that our current heapIndex should be
            #   the parent of our previous location
            heapIndex = parentIndex
            if (heapIndex %2 == 1):
                parentIndex = heapIndex//2
            else:
                parentIndex = (heapIndex//2) - 1

            # If the parentIndex is less than 0, it means we've hit the top, so we break the loop
            if (parentIndex < 0): 
                break

    # This function unfortunately runs in O(n) time. It takes in our working heap arrays, the networkIndex of our target node,
    #   and the value we want to change the node to. 
    def decreaseHeapItemKey(self, inputHeap, inputPointerArray, nodeNetworkIndex, newValue):
        # First we get the index of the input nodeNetworkIndex within our heap tree
        # These lists help us grab the index of an item in our pointerArray given a value. 
        nodeNetworkIndexes = list(inputPointerArray.values())
        heapLocationIndexes = list(inputPointerArray.keys())

        # If the node we were given is not in our heap, we need to insert that node. If it's there, 
        #   we find the heap location of that node and modify its value

        if (nodeNetworkIndexes.count(nodeNetworkIndex) == 0): # The count function runs in O(n) time
            self.insertToHeap(inputHeap, inputPointerArray, nodeNetworkIndex, newValue)
        else:
            nodeIndexArrayLocation = nodeNetworkIndexes.index(nodeNetworkIndex) # The index function runs in O(n) time
            nodeHeapIndex = heapLocationIndexes[nodeIndexArrayLocation]

            # We can't increase the value of our key, we can only decrease it. 
            if (newValue > inputHeap[nodeHeapIndex]):
                return
            else:
                inputHeap[nodeHeapIndex] = newValue
                # Since we've decreased a value in our tree, we may need to bubble up.
                self.bubbleUpBinaryHeap(inputHeap, inputPointerArray, nodeNetworkIndex, nodeHeapIndex, newValue)

    # This insert function runs in O(logn) time. It simply sticks in a new node as long as it hasn't been 
    #   previously seen in our priority queue before. 
    def insertToHeap(self, inputHeap, inputPointerArray, newNodeIndex, newValue):
        newHeapLocation = len(inputHeap)
        if (self.deletedIndexes[newNodeIndex] == 0): # If this node hasn't been deleted from our heap before...
            inputHeap[newHeapLocation] = newValue # We stick in our new value at the end of our tree. 
            inputPointerArray[newHeapLocation] = newNodeIndex # We update our pointer array with the new value
            self.bubbleUpBinaryHeap(inputHeap, inputPointerArray, newNodeIndex, newHeapLocation, newValue) # Then rebalance the tree

    # This bubbleDown function runs in O(logn) time. It is the reverse equivalent to bubbleUp, so this function is called
    #   when the point in question is the highest node. We compare our target node to its children and move if needed.
    def bubbleDownBinaryHeap(self, inputHeap, inputPointerArray, nodeNetworkIndex, nodeHeapIndex, value):

        leftChildHeapIndex = 1
        rightChildHeapIndex = 2

        # If we reach the bottom of our tree, set the child to our last node
        if (leftChildHeapIndex > len(inputHeap)-1):
            leftChildHeapIndex = len(inputHeap)-1
        if (rightChildHeapIndex > len(inputHeap)-1):
            rightChildHeapIndex = len(inputHeap)-1

        # Grab the children of our current Node and pick the one with the lowest value
        if (inputHeap[leftChildHeapIndex] < inputHeap[rightChildHeapIndex]):
            childHeapIndex = leftChildHeapIndex
        elif (inputHeap[rightChildHeapIndex] < inputHeap[leftChildHeapIndex]):
            childHeapIndex = rightChildHeapIndex
        else: 
            return
        
        # Now that we have our target childHeapIndex, we can compare the value at that index with the value in our nodeHeapIndex (value). 
        #   If the value of the child is less than our input value, then we bubble down.
        while (inputHeap[childHeapIndex] < value): 
            previousChildValue = inputHeap[childHeapIndex]
            inputHeap[childHeapIndex] = value
            inputHeap[nodeHeapIndex] = previousChildValue # Flip the values of the child and the replacing Node

            childNode = inputPointerArray[childHeapIndex]

            inputPointerArray[nodeHeapIndex] = childNode
            inputPointerArray[childHeapIndex] = nodeNetworkIndex # Flip the nodes our pointer array. 

            # Now that we've bubbled down one time, we get the next childHeapIndex based on the assumption that we are now the 
            #   child of our previous location
            nodeHeapIndex = childHeapIndex
            leftChildHeapIndex = (nodeHeapIndex * 2) + 1
            rightChildHeapIndex = (nodeHeapIndex * 2) + 2

            # If we reach the bottom of our tree, set the child to our last node
            if (leftChildHeapIndex > len(inputHeap)-1): 
                leftChildHeapIndex = len(inputHeap)-1
            if (rightChildHeapIndex > len(inputHeap)-1):
                rightChildHeapIndex = len(inputHeap)-1

            # Grab the children of our current Node and pick the one with the lowest value
            if (inputHeap[leftChildHeapIndex] < inputHeap[rightChildHeapIndex]):
                childHeapIndex = leftChildHeapIndex
            elif (inputHeap[rightChildHeapIndex] < inputHeap[leftChildHeapIndex]):
                childHeapIndex = rightChildHeapIndex
            else: 
                return

    # The deleteMin functin runs in O(logn) time. It takes in our heap arrays and pops off the lowest value, which will 
    #   by definition be at the top of the heap. It then brings the last node to the top and bubbles down.
    def deleteMinInHeap(self, inputHeap, inputPointerArray):
        
        removedNodeNetworkIndex = inputPointerArray[0]
        replacingNodeNetworkIndex = inputPointerArray[len(inputHeap)-1]

        # Override the first node with the last one and delete the remaining node
        replacingNodeValue = inputHeap[len(inputHeap) - 1]
        inputHeap[0] = replacingNodeValue
        del inputHeap[len(inputHeap) - 1]

        # Set the pointer array to reflect our switch
        inputPointerArray[0] = replacingNodeNetworkIndex
        del inputPointerArray[len(inputHeap)]
        self.deletedIndexes[removedNodeNetworkIndex] = 1

        if (self.heapIsNotEmpty(inputHeap)):
            self.bubbleDownBinaryHeap(inputHeap, inputPointerArray, replacingNodeNetworkIndex, 0, replacingNodeValue)        

        return removedNodeNetworkIndex

    # This check function runs in O(1) time
    def heapIsNotEmpty(self, inputHeap):
        if (len(inputHeap) == 0):
            return False
        else:
            return True

    # My driver code for the above priority queues...

    def getShortestPath( self, destIndex ):
        self.dest = destIndex

        if (self.nodeDistances[destIndex] == float('inf')):
            return {'cost':float('inf'), 'path':[]}
        
        path_edges = []
        total_length = 0
        currentNodeIndex = destIndex

        while currentNodeIndex != self.source:
            nextNodeIndex = -1

            nextNodeIndex = self.previousTracker[currentNodeIndex].node_id

            outputSource = self.network.nodes[nextNodeIndex]
            outputDestination = self.network.nodes[currentNodeIndex]
            for possibleEdge in outputSource.neighbors:
                if (possibleEdge.dest.node_id == currentNodeIndex):
                    outputEdge = possibleEdge
                    break
            path_edges.append( (outputSource.loc, outputDestination.loc, '{:.0f}'.format(outputEdge.length)) )
            
            currentNodeIndex = nextNodeIndex
        
        total_length = self.nodeDistances[destIndex]

        return {'cost':total_length, 'path':path_edges}

    def computeShortestPaths( self, srcIndex, use_heap=False ):
        self.source = srcIndex
        
        self.initializeDistanceArray(srcIndex)
        self.initializeTrackerArrays()

        # Setting up the base functions to use in Dijkstra's based on the chosen PQ Implementation

        if (use_heap): # Use the Heap Implementation
            heap = {}
            newPointerArray = {}
            self.initializeHeap(heap, newPointerArray)
            self.lastHeapNode = 0

            def decreaseKey(self, index, value):
                self.decreaseHeapItemKey(heap, newPointerArray, index, value)
            def deleteMin(self):
                return self.deleteMinInHeap(heap, newPointerArray)
            def isNotEmpty():
                return self.heapIsNotEmpty(heap)       

        else: # Use the Array Implementation
            priorityQueue = {}
            
            # Initialize our new priority queue with the source node
            self.insertToArray(priorityQueue, srcIndex, 0)
            
            def decreaseKey(self, index, value):
                self.decreaseArrayItemKey(priorityQueue, index, value)
            def deleteMin(self):
                return self.deleteMinInArray(priorityQueue)
            def isNotEmpty():
                return self.arrayIsNotEmpty(priorityQueue)

        # My Dijkstra's Implementation
            
        t1 = time.time()

        while (isNotEmpty()): # while the priority queue isn't empty (O(n))
            targetNodeIndex = deleteMin(self)
            targetNode = self.network.nodes[targetNodeIndex]
                
            for edge in targetNode.neighbors:
                edgeDestinationIndex = edge.dest.node_id
                destinationDistanceVal = self.nodeDistances[edgeDestinationIndex]
                potentialEdgeCost = self.nodeDistances[targetNodeIndex] + edge.length
                if (potentialEdgeCost < destinationDistanceVal):
                    # We found a better way to get to the edge index
                    self.nodeDistances[edgeDestinationIndex] = potentialEdgeCost
                    self.previousTracker[edgeDestinationIndex] = targetNode
                    decreaseKey(self, edgeDestinationIndex, potentialEdgeCost)

            # At this point, we have updated all of the node distances we could. 
        
        t2 = time.time()

        return (t2-t1)

