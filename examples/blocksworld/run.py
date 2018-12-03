#!/usr/bin/env python2.7

from __future__ import print_function

import os

from pddlstream.algorithms.search import solve_from_pddl
from pddlstream.algorithms.focused import solve_focused

from pddlstream.algorithms.incremental import solve_incremental
from pddlstream.utils import print_solution, read


def read_pddl(filename):
    directory = os.path.dirname(os.path.abspath(__file__))
    return read(os.path.join(directory, filename))

##################################################

def solve_pddl():
    domain_pddl = read_pddl('domain2.pddl')
    problem_pddl = read_pddl('problem2.pddl')

    plan, cost = solve_from_pddl(domain_pddl, problem_pddl)
    print('Plan:', plan)
    print('Cost:', cost)

##################################################

# TODO: could extract the FD parser by itself
# TODO: include my version of FD as a submodule

def main():
    solve_pddl()
    # solve_pddlstream()

if __name__ == '__main__':
    main()
