from pddlstream.language.constants import And
from pddlstream.language.stream import DEBUG
from pddlstream.algorithms.focused import solve_focused
from pddlstream.language.constants import Equal, AND, PDDLProblem
from pddlstream.utils import print_solution, read, INF, get_file_path, find_unique

import cProfile
import pstats

GRIPPER = 'gripper'
CUP = 'cup'
VANILLA = 'vanilla_cup'
STRAWBERRY = 'straw_cup'
NUTS = 'nuts_cup'

def create_problem(initial_poses):
    # coaster must move to goal
    initial_atoms = [
        ('IsEmpty', GRIPPER),
        ('CanMove', GRIPPER),
        ('HasVanilla', VANILLA),
        ('HasStraw', STRAWBERRY),
        ('HasNuts', NUTS)
    ]

    # final configuration
    goal_literals = [
        ('HasVanilla', CUP),
        ('HasStraw', CUP), 
        ('HasNuts', CUP)
    ]

    # add the is, at and tablesupport for each object
    for name, pose in initial_poses.items():
        if  GRIPPER in name:
            initial_atoms += [('IsGripper', name)]
        if  CUP in name:
            initial_atoms += [('IsCup', name)]
        initial_atoms += [('IsPose', name, pose), ('AtPose', name, pose), ('TableSupport', pose)]

    # read domain and stream files
    domain_pddl = read(get_file_path(__file__, 'domain.pddl'))
    stream_pddl = read(get_file_path(__file__, 'stream.pddl'))

    constant_map = {}
    stream_map = DEBUG
    # returns standard PDDL problem format
    return PDDLProblem(domain_pddl, constant_map, stream_pddl, stream_map,
                       initial_atoms, And(*goal_literals))


def main():
    # poses of all manipulatable objects
    initial_poses = {
        GRIPPER: (0., 15., 0.),
        CUP: (7.5, 0., 0.),
        VANILLA: (-10., 0., 0.),
        STRAWBERRY: (-15., 0., 0.),
        NUTS: (-5., 0., 0.)
    }

    problem = create_problem(initial_poses) # our own function to get the PDDL problem
    pr = cProfile.Profile()
    pr.enable()
    solution = solve_focused(problem, unit_costs=True, planner='ff-eager', debug=False, verbose=False) # max_planner_time=5,
    pr.disable()
    print_solution(solution)
    # pstats.Stats(pr).sort_stats('tottime').print_stats(10)

if __name__ == '__main__':
    main()