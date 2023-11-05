import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        """ 
            Basically, we are creating something like the below:
            [
                [False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False],
                [False, False, False, False, False, False, False, False]
            ]
        """
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        # Accessing the column. We add 2 since we are using range function.
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                """ 
                    Interesting implementation. It checks if it is
                    within bounds along with the mine check, probably
                    for terseness.
                """
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        # You could have also looked at the count instead of doing a 1-1 check.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.

    A cell is represented by the tuple (i,j) where i is the row 
    and j is the column of the mine field.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count
    
    def __hash__(self):
        return hash(self.count)

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.

        Here, we are dealing with pure logic. We are checking the conditions
        where we know for sure that a sentence's cells are safe. 
        """
        
        if self.count == len(self.cells):
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.

        Marking a mine means that we will update our sentence to remove
        the cell that we got from our set of cells and reduce the count by
        one since the count is about the number of mines.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            # We can do some edge case checking in case there is a sentence that
            # has a count of 0 but has a mine it in but let's not in this case.
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.

        Marking a cell safe is similar to marking it a mine, except that
        we would not change the count since the count is about the number of
        mines within those cells. 
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def get_neighbors(self, cell):
        """
            Since the specification won't let us change
            existing functions or arguments, I will 
            define a similar function to 
            "Minesweeper.nearby_mines" to get all the cells
            that are neighbors of a specific cell.
        """
        # Defining an empty set for neighbors
        neighbors = set()

        for i in range(cell[0] - 1, cell[0] + 2):        
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                
                # Make sure that cell is in bounds
                if 0 <= i < self.height and 0 <= j < self.width:
                    # Add the neigh 
                    neighbors.add((i, j))

        return neighbors

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        ## Step 1: Add the cell to the moves made
        self.moves_made.add(cell)


        ## Step 2: 
        #  2.1 - Mark the cell as safe by adding it to AI's knowledge
        self.safes.add(cell)

        #  2.2 - looping over sentences in our database to update them accordingly.
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
        

        ## Step 3
        #  3.1 - Get the neighbors of the given cell
        neigbors = self.get_neighbors(cell)

        # 3.2 - Create an initial sentence with the neighbors and count
        new_sentence = Sentence(neigbors, count)

        # 3.3 - Remove the known safe cells from the sentence
        for safe_cell in self.safes:
            new_sentence.mark_safe(safe_cell)

        # 3.4 - Remove the known mines from the sentence
        for mine in self.mines:
            new_sentence.mark_mine(mine)

        # 3.5 - Now that we have a clean sentence, let's append that to the knowledge base
        self.knowledge.append(new_sentence)


        ## Step 4
        # 4.1 - Create a larger set of safes and mines for potential infers from KB
        inferred_safes = set()
        inferred_mines = set()
        
        # 4.2  - Once we find any known safes or mines, we want to remove that sentence
        # since that sentence loses its use for us.
        sentences_to_remove = set()

        # 4.3 - Get any existing inferments we can make from existing KB
        for sentence in self.knowledge:
            # Grabbing the known safes and mines
            known_safes = sentence.known_safes()
            known_mines = sentence.known_mines()
            
            # Checking if any safes or mines were returned
            if known_safes:
                for known_safe in known_safes:
                    inferred_safes.add(known_safe)
                sentences_to_remove.add(sentence)

            if known_mines:
                for known_mine in known_mines:
                    inferred_mines.add(known_mine)
                sentences_to_remove.add(sentence)

        # 4.4 - Add the new information to AI's knowledge
        if len(inferred_safes) > 0:
            for safe in inferred_safes:
                self.safes.add(safe)
        
        if len(inferred_mines) > 0:
            for mine in inferred_mines:
                self.mines.add(mine)

        # 4.5 - Removing the sentences who served their purpose
        if len(sentences_to_remove) > 0:
            for sentence in sentences_to_remove:
                self.knowledge.remove(sentence)


        ## Step 5
        # 5.1 - Let's create a new set that will contain all the subsets we can infer
        subsets = set()
        sentences_to_add = set()

        # 5.2 - Let's loop over all our knowledge and see what we can get from our KB
        KB = self.knowledge
        for i in range(len(KB)):
            for j in range(i+1, len(KB)):
                # Checking if cells of sentence i form subset of cells of sentence j
                if KB[i].cells.issubset(KB[j].cells):
                    subsets.add((i, j))
                # Checking if cells of sentence j form subset of cells of sentence i
                elif KB[i].cells.issuperset(KB[j].cells):
                    subsets.add((j, i))

        # 5.3 - Once we have all the subsets, let's construct some new knowledge
        if len(subsets) > 0:
            for subset in subsets:
                i, j = subset
                """ 
                    We are using the '-' method instead of 'difference_update' since
                    that method creates a new set without modifying the original sets.

                    We can also just work with indices because knowledge is a list, 
                    not a set which means that it is ordered and indices matter.
                """
                new_cells = KB[j].cells - KB[i].cells
                new_count = KB[j].count - KB[i].count

                if new_count < 0:
                    print(KB[i])
                    print(KB[j])
                    raise Exception("Something is wrong with the subsets. Check Minesweeper, line 360")
                
                new_sentence = Sentence(new_cells, new_count)
                
                # Best not to add this to KB as we are working with KB
                sentences_to_add.add(new_sentence)
        
        # 5.4 - Let's add all the sentences we got to our KB
        if len(sentences_to_add) > 0:
            for sentence in sentences_to_add:
                KB.append(sentence)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        # Let's return a move from safe moves that hasn't been made.
        for safe_cell in self.safes:
            if safe_cell not in self.moves_made:
                return safe_cell



    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Let's get board height and width
        board_height = self.height
        board_width = self.width
        
        # This will help break out of the loop. We are getting
        # max loop possible
        moves_available = board_height * board_width
        
        # Let's keep doing it until we break out of the loop
        while True:
            # Let's select a random move
            i = random.randrange(board_height)
            j = random.randrange(board_width)
            random_move = (i, j)

            # Let's return it if it's not been chosen yet or
            # it is not a mine.
            if random_move not in self.moves_made and random_move not in self.mines:
                return random_move
            else:
                # Reducing a move checked from the maximum moves possible
                moves_available -= 1
            
            # If no more moves are left, exiting the loop.
            if moves_available == 0:
                return None
            
                