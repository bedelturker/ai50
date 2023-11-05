import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {
        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Grabs a set with keys from the people dictionary.
    names = set(people)
    # Loop over all sets of people who might have the trait
    """
        'have_trait' basically refers to all subsets combinations.
        It starts off with everyone and then skips the ones
        that 'fail the evidence' that they have the trait given
        that their trait information is known.
    """
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue
        
        """
            Now we know that everyone in the combination that have
            made it thus far have either have the or has unknown
            information, we can look at the subset again and grab
            other information.

        """
        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            """
                Removing any set that contains 'one_gene' that we selected above.
                The idea here is that if someone carries one copy of the gene,
                they cannot carry two copies of the gene.
            """
            for two_genes in powerset(names - one_gene):
                # # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
    1 - everyone in set `one_gene` has one copy of the gene, and
    2 - everyone in set `two_genes` has two copies of the gene, and
    3 - everyone not in `one_gene` or `two_gene` does not have the gene, and
    4 - everyone in set `have_trait` has the trait, and
    5 - everyone not in set` have_trait` does not have the trait.

    - Calculate probabilities for each of the cases above.
    - Multiply all probabilities

    """
    
    ## VARIABLES
    p_one_gene = 1
    p_two_genes = 1
    p_no_gene = 1
    p_trait = 1
    p_no_trait = 1


    ## STEP 1 - Person in one gene having one gene
    # First check that one_gene set has people in it.
    if len(one_gene) > 0:
        for person in one_gene:
            mother = people[person]["mother"]
            father = people[person]["father"]
            # Check if they have a mother or father
            if mother is not None:
                # Both mother and father has one gene
                if mother in one_gene and father in one_gene:
                    p_one_gene = (0.49 * 0.99) + (0.01 * 0.01)
                # Mother has one gene; father has no gene
                if mother in one_gene and father not in one_gene and father not in two_genes:
                    p_one_gene = (0.49 * 0.99) + (0.01 * 0.01)
                # Father has one gene; mother has no gene
                if mother not in one_gene and mother not in two_genes and father in one_gene:
                    p_one_gene = (0.01 * 0.01) + (0.49 * 0.99)

                # Neither father nor mother has the gene
                if mother not in one_gene and mother not in two_genes and father not in one_gene and father not in two_genes:
                   p_one_gene = 0

                # Both have two genes
                if mother in two_genes and father in two_genes:
                    p_one_gene = 1 - ((0.01 * 0.01) + (0.01 * 0.01))

                # Mother has two genes, father has no genes
                if mother in two_genes and father not in one_gene and father not in two_genes:
                    p_one_gene = (0.99 * 0.99) + (0.01 * 0.01)

                # Father has two genes, mom has no genes
                if mother not in one_gene and mother not in two_genes and father in two_genes:
                    p_one_gene = (0.01 * 0.01) + (0.99 * 0.99)

            # Calculate values for people with no parents
            else:
                p_one_gene = PROBS["gene"][1]
                
    ## STEP 2 - Person having two genes
    if len(two_genes) > 0:
            for person in one_gene:
                mother = people[person]["mother"]
                father = people[person]["father"]
            
            # Check if they have a mother or father
            if mother is not None:
                
            else:
                p_one_gene = PROBS["gene"][2]


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    raise NotImplementedError


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
