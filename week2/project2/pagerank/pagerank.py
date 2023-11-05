import os
import random
import re
import sys
import copy
import math

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        # ":.4f" allows f-string to be formatted to
        # allow float values to have four indices.
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            # This is basically excluding the filename from the set of links
            # if it's found there. This also means that there is only one 
            # link to each page per document. There cannot be a page that
            # has two hyperlinks in another page.
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    ## STEP 1 
    """ 
        We will begin by grabbing the links that are on our current
        page using current page as a key in our corpus.
    """
    links = corpus[page]

    ## STEP 2
    """
        Create a copy of corpus so that we can modify the dictionary
        and add probability values to it. This way, we can store this
        information. 
        Note that corpus_p stands for probabilities in corpus.
    """
    corpus_p = copy.deepcopy(corpus)

    # We will start with 0 probability for each value by replacing the values
    # of keys in corpus.
    for link in corpus_p:
        corpus_p[link] = 0
    
    ## STEP 3
    """
        Given a dampening factor (d), there will always be a default probability
        of selecting any page from the corpus, including the page we are on.
        Hence we will add that probability to each.
    """
    # Total random selection
    undamped = 1 - damping_factor

    # Total count of links in corpus
    corpus_count = len(corpus_p)

    # Probability of being selected for each link is equal
    undamped_p_each = undamped/corpus_count

    # Setting the random selection probability to each link's 
    # probability since they are 0.
    for link in corpus_p:
        corpus_p[link] = undamped_p_each


    ## STEP 4
    """
        As a last step, we need to add the damped part to the 
        probabilities. This would only include the links on the
        current page.
    """
    links_count = len(links)

    # If a page has no link, then we act as if it has links 
    # to all pages, which means that links_count = corpus_count
    if links_count == 0:
        links_count = corpus_count

    # Each link has the same chance of being selected
    damped_p_each = damping_factor/links_count

    # We need to add the damped probability to distributed
    # undamped probability in corpus_p. We will only add
    # to links found on the page.
    for page in corpus_p:
        if page in links:
            current_probability = corpus_p[page]
            corpus_p[page] = current_probability + damped_p_each
    return corpus_p


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    ## STEP 1
    """ 
        Let's define two variables to hold our states. We will
        need states for the following:
            1 - A way to keep track of how many pages we have visited.
                We will use this number to compare against sample size 'n'
                so that we can know when to stop.
            2 - A dictionary to store how many times we have visited a
                specific page from the corpus.
    """
    pages_visited = 0
    corpus_visits = copy.deepcopy(corpus)
    # Setting initial counts to 0.
    for page in corpus_visits:
        corpus_visits[page] = 0

    ## STEP 2
    """ 
        We will select an initial page randomly without transition
        model since we don't have any 'current' page.
    """
    # Making a list of all pages in corpus
    pages_list = list(corpus.keys())

    """
        Making a random selection with equal probability based on the list
        Since we are not using any weights, it is better to use random.choice
        instead of random.choices since it returns one object.
    """
    first_page = random.choice(pages_list)

    # Setting current page for the first time
    current_page = first_page

    # Adding to the count of the page chosen
    corpus_visits[current_page] = 1

    # Increasing visited pages count
    pages_visited += 1
        

    ## STEP 3
    """
        We need to define a loop whereby we increase pages_visited
        as we choose to visit a page depending on whether we will
        choose at random or will use the links. 

        Initially, if we have not visited any page, we will choose
        one at random. Then, we will increase the count of that 
        page in our corpus_visits. 

        After for all of them, we will keep using the transition
        model and make a selection accordingly until we reach the
        desired sample count.
    """
    # Going through all the pages until we reach desired sample size 
    while pages_visited < n:
            # Grabbing probability of visiting a page given a current page
            probability_distribution = transition_model(corpus, current_page, damping_factor)
            
            # Getting the list of pages and their probabilies separately to pass to random function.
            list_pages = list(probability_distribution.keys())
            list_probabilities = list(probability_distribution.values())
            
            # Getting the next page to visit based on the probabilities
            next_page = random.choices(list_pages, list_probabilities)[0]

            # Setting the current page to next page (i.e. visiting the page)
            current_page = next_page

            # Getting the current count of the visited page.
            current_page_count = corpus_visits[current_page]

            # Increasing the count of the current page
            corpus_visits[current_page] = current_page_count + 1

            # Increasing the count of visited pages in total
            pages_visited += 1

    ## STEP 4
    """
        Now that we have a dictionary with all the counts, 
        we can create a new dictionary where we will replace the
        values with probabilities given a sample size n.

        We are creating a copy because changing a dictionary while
        looping over it can cause issues.

        This will essentially represent our PageRank values.
    """
    page_ranks = copy.deepcopy(corpus_visits)
    """
        Let's loop over each page in corpus_visits and divide the
        count there by total sample size to get the ratio, which
        we can record as our PageRank for that page in page_ranks.
    """
    for page in corpus_visits:
        page_count = corpus_visits[page]
        page_rank = page_count / n
        
        # Let's grab the page in page_ranks and update its values
        page_ranks[page] = page_rank
    
    ## STEP 5
    # Checking that ranking values add up to 1 before returning
    ranks_total = 0
    for page in page_ranks:
        ranks_total += page_ranks[page]
    
    # Checking if they are equal up to this number. 
    # There can be small variations given the issues with floating
    # point arithmetic
    if math.isclose(ranks_total, 1, abs_tol=0.00001):
        return page_ranks
    else:
        raise Exception(f"Check your sample ranking. Sum of all ranks should be 1. You've got {ranks_total}")


def page_rank_algorithm(corpus, current_ranks, desired_page, damping_factor):
    """
        This is a helper function we are defining to
        calculate the result of page_rank_algorithm.
        The main calculation is to find the sum of all 
        pages where page 'i' has a link to current_page 
        that has been passed in the function's arguments.

        For each linked page, we will look at its own
        PageRank, divide by number of links and add 
        everything up.
    """
    ## STEP 1
    linked_pages_sum = 0
    linked_pages = {}
    
    """
        Adding all the pages with links to desired_page along with 
        total number of links that they reference.

        However, we will first check if a page has no links. If yes,
        then we will assume a link to the direct page and say that 
        total number of links it has is equal to the number of pages
        in the corpus since having no links is assumed to be the same 
        as having links to all pages.
    """
    for page in corpus:
        # Making sure that we are not counting the page we are already on.
        if desired_page is not page:
            # Checking separately for the case where a page has no links
            if len(corpus[page]) == 0:
                linked_pages[page] = len(corpus)
            
            elif desired_page in corpus[page]:
                linked_pages[page] = len(corpus[page])

    ## STEP 2
    """
        Now, we need to get the probability of visiting the desired
        page from each linked page by dividing the probability of 
        visiting the linked page (PageRank(i)) by number of links
        it has.
    """
    for page in linked_pages:
        visit_probability = current_ranks[page] / linked_pages[page]
        linked_pages_sum += visit_probability
    

    ## STEP 3
    """
        Now we can do the calculate the result of PageRank. 
        The full formula is
            PR(A) = ((1-d)/N) + d * linked_pages_sum
        where d is dampening factor and N is the number of
        pages in corpus
    """
    page_count = len(corpus)

    page_rank = ((1 - damping_factor) / page_count) + (damping_factor * linked_pages_sum)
    
    return page_rank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    ## STEP 1
    """
        Once again, let's begin by defining the basic variables
        that we will use. We will define:
            1 - Total number of pages in corpus
            2 - A new dictionary where we will keep track of the
                page ranks.
            3 - A second dictionary where we can keep the previous
                rankings and compare values. Initially, previous
                ranks will be an empty dictionary.
            4 - Highest Deviation Factor - a number that represents
                how much the PageRank of a page has changed from last
                iteration. We will initally set it to negative infinity
                to be the highest value so that any value will be higher
                than that initially.
    """
    page_count = len(corpus)
    current_ranks = copy.deepcopy(corpus)
    previous_ranks = {}
    
    # Setting initial ranks to 1/N where N represents page count
    for page in current_ranks:
        current_ranks[page] = 1 /page_count

    ## STEP 2
    """
        We need to create an infinite loop whereby we continue to calculate
        PageRank values of each page until highest deviation of each page
        is not more than 0.001. Then, we will exit the loop
    """
    run_count = 0
    while True:
        # Begin by creating a new dictionary where we will update the values
        new_ranks = copy.deepcopy(current_ranks)

        # Loop over values in current_ranks and update values in new ranks
        for page in current_ranks:
            new_ranks[page] = page_rank_algorithm(corpus, current_ranks, page, damping_factor)
        

        # Assign current ranks to previous ranks and new ranks to current ranks
        previous_ranks = copy.deepcopy(current_ranks)
        current_ranks = copy.deepcopy(new_ranks)

        """
            The idea below is to check if there are any pages that have a deviation
            of more than 0.001 between its current and previous ranking.

            If yes, we continue the loop. If no, we stop. We need to use absolute 
            values since deviation can be in both directions

        """
        total_deviations = 0
        for page in current_ranks:
            if abs(current_ranks[page] - previous_ranks[page]) > 0.001:
                total_deviations += 1
                run_count += 1
        
        if total_deviations == 0:
            run_count += 1
            return current_ranks


if __name__ == "__main__":
    main()
