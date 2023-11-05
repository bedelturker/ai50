import sys

""" 
    We are defining Nodes which will represent
    our states, including our initial state and 
    transitional models (states) that we will
    explore.

    Note that each state (or Node) keeps track of
    four specific things:
        - State: What is the state that this node represents?
        - Parent node: What was the node preceding this node?
        - Action: What specific action that we took from the parent node that led to this node?
        - Path cost: What was the total cost of all the actions that led to this node?
"""
class Node():
    """ 
        '__init__' allows to define attributes that only belong to a specific instant of a class.
        Basically, we are saying that when we initially an instance of this entity as Node('B', 'A', 'swipe-right'),
        we are saying that'B' represents the state of this node, 'A' is its parent, and 
        'swipe-right' is the action we took to get from 'A' to 'B'.
    """
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action

"""
    'Frontier' represents the range of possibilities that remain to be explored. When we start out, 
    Frontier consists solely of the initial state. Then, as we explore each node, more possibilities
    are added to the stack based on the nodes that can lead from the node under exploration.

    Note that the below represents a 'stack' frontier, meaning a frontier where the node that was last
    added is removed first. This 'last-in first-out' method is used for 'depth-first search (DFS)' as
    opposed to 'breadth-first search (BFS)' where we implement a 'first-in first-out' methodology.
"""
class StackFrontier():
    # We are initializing these attributes with this constructor since their values will not be shared with other instances.
    def __init__(self):
        self.frontier = []

    # Function to add a node to the frontier that has been passed as an argument to this method.
    def add(self, node):
        self.frontier.append(node)
    
    # Function to see if a specific state exists in any of the nodes in the frontier. It returns a 'True' or 'False' value.
    def contains_state(self, state):
        return any(state == node.state for node in self.frontier)
    
    # Function to check if the frontier has become empty (meaning search is over). It returns a 'True' or 'False' value.
    def check_empty(self):
        return len(self.frontier) == 0

    # Function to remove a node from the frontier. We don't pass a specific node since we don't want any node to be removable.
    # We specifically want the node that was added last to be removed.
    def remove(self):
        # Making sure that the frontier is not empty
        if self.check_empty():
            raise Exception("Empty Frontier")
        else:
            # We can simply grab and remove the last item in the list like this.
            return self.frontier.pop()
        

""" 
    We can implement a 'first-in first-out (FIFO)' search process as well by simply tweaking the way we remove the nodes.
    Below, we pass the class we created above into our new entity allowing it to adopt its attributes while giving us
    the flexibility to change a specific method, in this case '.remove()'
"""
def QueueFrontier(StackFrontier):
    def remove(self):
        if self.check_empty():
            raise Exception("Empty Frontier")
        else:
            # Note that we are grabbing the first item by specifying its position in the list, i.e. '0'.
            return self.frontier.pop(0)

        
""" 
    Below we are defining a 'Maze' object that gets created
    from a '.txt' file with spaces for paths, '#' for walls,
    and a start point 'A' along with an end point 'B'.
"""
class Maze():
    # '__init__' function takes a filename because we need the
    # file to be able to create the object itself.
    def __init__(self, filename):
        with open(filename) as f:
            contents = f.read()

        # We need to validate the file first to ensure that it has 
        # the right characteristics for our object.
        if contents.count('A') != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")
        
        # We need to then determine the height and width of the maze by
        # breaking the contents of the file at the text lines into an array (list)
        # of strings.
        contents = contents.splitlines()
        """
            In order to explain what's going on, let's consider a simpler maze with
            three lines:

                ####B#
                ###  #
                ###A##

            When we split lines, the above becomes contents = ["####B#", "###  #", "###A##"]    
        """
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Keeping track of the walls
        self.walls = []
        """
            Here we use range because we want the value of the iterative 'i'
            to be an integer like 1 or 2. If we said, for i in self.height, 
            the value of i would be "####B#" for instance wherease we want it
            to be 0. 

            When we say range(self.height), we get (0, 3) and the iterated values 
            are: '0, 1, 2". 
        """
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    # We are locating the start of the maze and not adding that to the
                    # rows.
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    
                    # Locating the goal
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    
                    # Locating the paths in the maze
                    elif contents[i][j] == " ":
                        row.append(False)
                    
                    # Only adding the specific points where a wall exists, i.e. where
                    # the hashtags are. We could have just added that as well but we 
                    # want to locate the start and end as well, which led to this code.
                    else:
                        row.append(True)

                except IndexError:
                    row.append(False)
            
            self.walls.append(row)
        self.solution = None
    
    def terminal_output(self):
        solution = self.solution[1] if self.solution is not None else None
        # The code below prints an empty line
        print()
        """
            'enumerate' function below is basically returning a tupple that 
            gives us the index of an item in a list along with its value in
            the (index, value) format.
        """
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                # With this double loop, we are basically recreating the text
                # file in the terminal.
                if col:
                    # Note that we are saying that Python should not pass the default
                    # \n character for a new line so that we can keep adding the items.
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                # Here, we are basically putting a '*' in all remaining spaces if a solution
                # has been found.
                elif (solution is not None and (i, j) in solution):
                    print("*", end="")
                # If not, we are printing spaces
                else:
                    print(" ", end="")
            # Allows us to pass on to the next line
            print() 
        print()

    # Below we are defining all hte possible paths that one can take.
    # In other words, neighbors are all nodes that we can expand into.
    def neighbors(self, state):
        # We are assigning the row and column numbers from the state tuple that
        # has the position of the state. 
        row, col = state
        # We are defining all the possible actions.
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            # For each of the actions possible in a given state, we are seeing the
            # action name and its result in the above code. We are then attaching
            # the possible results to the result list with the name of the action.
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                # Resulting list is a tuple with action and resulting state from that action
                result.append((action, (r, c)))
        return result
    
    def solve(self):
        """Finds a solution to maze, if one exists."""

        # Keep track of number of states explored
        self.num_explored = 0

        # Initialize frontier to just the starting position
        start = Node(state=self.start, parent=None, action=None)
        frontier = StackFrontier()
        frontier.add(start)

        # Initialize an empty explored set
        self.explored = set()

        # Keep looping until solution found
        while True:

            # If nothing left in frontier, then no path
            if frontier.check_empty():
                raise Exception("no solution")

            # Choose a node from the frontier
            node = frontier.remove()
            self.num_explored += 1

            # If node is the goal, then we have a solution
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            # Mark node as explored
            self.explored.add(node.state)

            # Add neighbors to frontier
            for action, result_state in self.neighbors(node.state):
                if not frontier.contains_state(result_state) and result_state not in self.explored:
                    child = Node(state=result_state, parent=node, action=action)
                    frontier.add(child)
    
    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw
        cell_size = 50
        cell_border = 2

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                # Walls
                if col:
                    fill = (40, 40, 40)

                # Start
                elif (i, j) == self.start:
                    fill = (255, 0, 0)

                # Goal
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)

                # Solution
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)

                # Explored
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # Empty cell
                else:
                    fill = (237, 240, 252)

                # Draw cell
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        img.save(filename)

    if len(sys.argv) != 2:
        sys.exit("Usage: python maze.py maze.txt")

m = Maze(sys.argv[1])
print("Maze:")
m.terminal_output()
print("Solving...")
m.solve()
print("States Explored:", m.num_explored)
print("Solution:")
m.terminal_output()
m.output_image("maze.png", show_explored=True)