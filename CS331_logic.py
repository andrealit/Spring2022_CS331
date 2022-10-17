from sympy import *
import string


#################################################################
# Knowledge Base
#################################################################

class KB:

    """
        Knowledge base containing non-duplicate expressions in CNF form.
        Capital letters A-Z are available as symbols. (Note that E does not work.)
        Implies: >>. Or: |. And: &. Not: ~.
    """


    def __init__(self):
        self.expressions = []


    def addExpr(self, expr):
        """
            Adds string expr to knowledge base if it does not duplicate or contradict
            previous statements. 
        """

        # Convert to CNF form
        cnf = to_cnf(sympify(expr), simplify=True)

        # Separate & expression into clauses
        if isinstance(cnf, And):
            cnf = list(cnf.args)
        else:
            cnf = [cnf]

        # Consider adding each expression to KB
        for e1 in cnf:
            for e2 in self.expressions:
                if Equivalent(e1, e2)==True:
                    print("Already in KB")
                    return 
                elif not simplify((e1) & (e2)):
                    print("Contradicts statement in KB")
                    return
            self.expressions.append(e1)
            print("Added " + expr + " to KB")


    def removeExpr(self, expr):
        """
            Removes string expr or equivalent expressions from the knowledge base.
            Note: assumes that expressions are clauses.
        """
        e1 = to_cnf(sympify(expr), simplify=True)
        for e2 in self.expressions:
            if Equivalent(e1, e2)==True:
                self.expressions.remove(e2)
                print("Expression " + expr + " removed from KB")
                return
        print("Expression " + expr + " not found in KB")


    def print(self):
        print("Knowledge Base:")
        for c in self.expressions:
            print(c)

    



#################################################################
# Resolution algorithm
#################################################################


def query(kb, expr):
    """
        Wrapper function for resolution. Does knowledgebase
        kb entail expression expr?
    """
    print("Query: " + expr)
    entailed = resolution(kb, sympify(expr))
    print()
    if entailed:
        print("KB entails " + expr)
    else:
        print("KB does not entail " + expr)


def resolution(kb, expr):
    """
        Resolution algorithm. New clauses are printed as resolution occurs.
        A false negative can occur if more than 1000 iterations are required.
    """

    ITERATION_LIMIT = 1000
    iterations = 0

    # Convert KB & ~expr to CNF form
    cnf = to_cnf(~expr, simplify=True)
    
    # Separate & expression into clauses
    if isinstance(cnf, And):
        cnf = list(cnf.args)
    else:
        cnf = [cnf]
    
    clauses = cnf + kb.expressions.copy()
    new = []
    
    i = 0
    j = 1
    while iterations < ITERATION_LIMIT:
        
        # Attempt resolution for every pair of clauses
        while i<len(clauses)-1:
            while j<len(clauses):

                # Resolve clause
                resolvent = resolve(clauses[i], clauses[j])
           
                # Two clauses resolve to an empty clause => expr is entailed
                if not resolvent:
                    return True

                # Add resolved clause to known clauses if it is not already present
                elif resolvent != True: # indicates clauses cannot be resolved
                    duplicate = inList(clauses, resolvent) | inList(new, resolvent)
                    if not duplicate:
                        new.append(resolvent)
                        print(resolvent)
                j+=1
            i+=1
            j=i+1

        # No clauses can be added => expression is not entailed
        if not new:
            return False

        # Update for next iteration
        else:
            clauses = new + clauses
            new = []
            iterations +=1
            i=0
            j=1
    print("Timed out")
 


def resolve(C1, C2):
    """
        Resolve 2 clauses. Note that there may be more efficient
        ways to do this.
    """

    # Mutually exclusive clauses
    if simplify(C1 & C2) == False:
        return False

    # Compare literals in C1 and C2 to determine if resolution is possible
    elim_list = []
    new_expr = False

    if isinstance(C1, Or):
        list1 = list(C1.args)
    else:
        list1 = [C1]
    if isinstance(C2, Or):
        list2 = list(C2.args)
    else:
        list2 = [C2]

    for l1 in list1:
        included = True
        for l2 in list2:
            if not simplify(l1 & l2):
                elim_list.append(l2)
                included = False
        if included:
            new_expr = new_expr | l1

    # Resolve clauses, if possible
    if len(elim_list) > 0:
        for l2 in list2:
            if l2 not in elim_list:
                new_expr = new_expr | l2
        return new_expr

    # Clauses could not be resolved
    return True


def inList(l, expr):
    """
        Helper function that checks if logic expression expr is in list l.
    """
    for c in l:
        if Equivalent(c, expr)==True:
            return True
    return False



def loadDefaultKB():
    kb = KB() 
    kb.addExpr('K | H')
    kb.addExpr('V | R')
    kb.addExpr('~H | K')
    kb.addExpr('~V | H')
    kb.addExpr('~R | ~V')
    return kb


if __name__ == "__main__":
    kb = loadDefaultKB()
    print()
    kb.print()
    print()  
    query(kb, 'K')


#print(resolve(sympify('A|~D|~C'), sympify('B|D|C')))

