#!/usr/bin/env python

from __future__ import print_function

import cProfile
import pstats
import argparse
import pybullet as p

from examples.pybullet.utils.pybullet_tools.kuka_primitives import BodyPose, BodyConf, Command, get_grasp_gen, \
    get_stable_gen, get_ik_fn, get_free_motion_gen, \
    get_holding_motion_gen, get_movable_collision_test
from examples.pybullet.utils.pybullet_tools.utils import WorldSaver, connect, dump_world, get_pose, set_pose, Pose, \
    Point, set_default_camera, stable_z, wait_for_duration, get_image, \
    BLOCK_URDF, get_configuration, SINK_URDF, STOVE_URDF, load_model, is_placement, get_body_name, \
    disconnect, DRAKE_IIWA_URDF, get_bodies, user_input, HideOutput, R2D2_URDF
    
from pddlstream.algorithms.focused import solve_focused
from pddlstream.language.generator import from_gen_fn, from_fn, empty_gen
from pddlstream.language.synthesizer import StreamSynthesizer
from pddlstream.utils import print_solution, read, INF, get_file_path, find_unique

USE_SYNTHESIZERS = False

NIRYO_ONE = "/home/suddhu/software/pddlstream/my-models/niryo_one_description/urdf/v2/niryo_one.urdf"

def get_fixed(robot, movable):
    rigid = [body for body in get_bodies() if body != robot]
    fixed = [body for body in rigid if body not in movable]
    return fixed

def place_movable(certified):
    placed = []
    for literal in certified:
        if literal[0] == 'not':
            fact = literal[1]
            if fact[0] == 'trajcollision':
                _, b, p = fact[1:]
                set_pose(b, p.pose)
                placed.append(b)
    return placed

def get_free_motion_synth(robot, movable=[], teleport=False):
    fixed = get_fixed(robot, movable)
    def fn(outputs, certified):
        assert(len(outputs) == 1)
        q0, _, q1 = find_unique(lambda f: f[0] == 'freemotion', certified)[1:]
        obstacles = fixed + place_movable(certified)
        free_motion_fn = get_free_motion_gen(robot, obstacles, teleport)
        return free_motion_fn(q0, q1)
    return fn

def get_holding_motion_synth(robot, movable=[], teleport=False):
    fixed = get_fixed(robot, movable)
    def fn(outputs, certified):
        assert(len(outputs) == 1)
        q0, _, q1, o, g = find_unique(lambda f: f[0] == 'holdingmotion', certified)[1:]
        obstacles = fixed + place_movable(certified)
        holding_motion_fn = get_holding_motion_gen(robot, obstacles, teleport)
        return holding_motion_fn(q0, q1, o, g)
    return fn

#######################################################

def pddlstream_from_problem(robot, movable=[], teleport=False, movable_collisions=False, grasp_name='side'):
    #assert (not are_colliding(tree, kin_cache))
    domain_pddl = read(get_file_path(__file__, 'domain1.pddl'))
    stream_pddl = read(get_file_path(__file__, 'stream1.pddl'))
    constant_map = {}

    print('Robot:', robot)
    conf = BodyConf(robot, get_configuration(robot))
    init = [('CanMove',),
            ('Conf', conf),
            ('AtConf', conf),
            ('HandEmpty',),
            ('Cleaned',)]

    fixed = get_fixed(robot, movable)

    # movable_bodies = [tub_straw, tub_vanilla, scoop_vanilla, scoop_straw, bowl, wash]
    tub_straw = movable[0]
    tub_vanilla = movable[1]
    vanilla_scoop = movable[2]
    straw_scoop = movable[3]
    bowl = movable[4]
    wash = movable[5]
    
    print('Movable:', movable)
    print('Fixed:', fixed)
    for body in movable:
        pose = BodyPose(body, get_pose(body))
        init += [('Graspable', body),
                 ('Pose', body, pose),
                 ('AtPose', body, pose)]
        for surface in movable:
            if body != surface:
                init += [('Stackable', body, surface)]
                if is_placement(body, surface):
                    init += [('Supported', body, pose, surface)]

    init += [('isEmpty',)]
    init += [('Bowl', bowl)]
    init += [('VanillaScoop', vanilla_scoop)]
    init += [('StrawScoop', straw_scoop)]
    init += [('Wash', wash)]
    goal = ('and',
            ('AtConf', conf),

            ('First', straw_scoop, bowl),

            ('Second', vanilla_scoop, straw_scoop),

            # ('Second', vanilla_scoop, straw_scoop),
    )

    stream_map = {
        'sample-pose': from_gen_fn(get_stable_gen(fixed)),
        'sample-grasp': from_gen_fn(get_grasp_gen(robot, grasp_name)),
        'inverse-kinematics': from_fn(get_ik_fn(robot, fixed, teleport)),
        'plan-free-motion': from_fn(get_free_motion_gen(robot, fixed, teleport)),
        'plan-holding-motion': from_fn(get_holding_motion_gen(robot, fixed, teleport)),
        'TrajCollision': get_movable_collision_test(),
    }

    if USE_SYNTHESIZERS:
        stream_map.update({
            'plan-free-motion': empty_gen(),
            'plan-holding-motion': empty_gen(),
        })

    return domain_pddl, constant_map, stream_pddl, stream_map, init, goal


#######################################################

def load_world():
    # TODO: store internal world info here to be reloaded
    with HideOutput():
        robot = load_model(DRAKE_IIWA_URDF)
        # robot = load_model(NIRYO_ONE)
        floor = load_model('models/short_floor.urdf')
        tub_straw = load_model('models/tub_straw.urdf', fixed_base=False )
        tub_vanilla = load_model('models/tub_vanilla.urdf', fixed_base=False )
        bowl = load_model('models/bowl.urdf', fixed_base=False)
        scoop_vanilla = load_model('models/vanilla_scoop.urdf', fixed_base=False)
        scoop_straw = load_model('models/straw_scoop.urdf', fixed_base=False)
        wash = load_model('models/tub_wash.urdf', fixed_base=False)

    body_names = {
        tub_straw: 'tub_straw',
        tub_vanilla: 'tub_vanilla',
        scoop_vanilla: 'scoop_vanilla',
        scoop_straw: 'scoop_straw',
        bowl: 'bowl',
        wash: 'wash',
    }
    
    movable_bodies = [tub_straw, tub_vanilla, scoop_vanilla, scoop_straw, bowl, wash]
    set_pose(tub_straw, Pose(Point(x=0.5, y=-0.5)))
    set_pose(tub_vanilla, Pose(Point(x=+0.5, y=+0.0)))
    set_pose(scoop_straw, Pose(Point(x=0.5, y=-0.5, z=stable_z(scoop_straw, tub_straw))))
    set_pose(scoop_vanilla, Pose(Point(x=+0.5, y=+0.0, z=stable_z(scoop_vanilla, tub_vanilla))))
    set_pose(wash, Pose(Point(x=-0.5, y=+0.0)))
    set_pose(bowl, Pose(Point(y=+0.5, z=0.2)))
    set_default_camera()

    return robot, body_names, movable_bodies

def postprocess_plan(plan):
    paths = []
    for name, args in plan:
        if name  == 'dump_first':
            paths += args[-1].reverse().body_paths
        elif name  == 'dump_second':
            paths += args[-1].reverse().body_paths
        elif name in ['move', 'move_free', 'move_holding', 'scoop_vanilla', 'scoop_straw']:
            paths += args[-1].body_paths
    return Command(paths)

#######################################################

def main(viewer=False, display=True, simulate=False, teleport=False):
    # TODO: fix argparse & FastDownward
    #parser = argparse.ArgumentParser()  # Automatically includes help
    #parser.add_argument('-viewer', action='store_true', help='enable viewer.')
    #parser.add_argument('-display', action='store_true', help='enable viewer.')
    #args = parser.parse_args()
    # TODO: getopt

    connect(use_gui=viewer)
    robot, names, movable = load_world()
    saved_world = WorldSaver()
    #dump_world()

    pddlstream_problem = pddlstream_from_problem(robot, movable=movable,
                                                 teleport=teleport, movable_collisions=True)
    _, _, _, stream_map, init, goal = pddlstream_problem
    synthesizers = [
        StreamSynthesizer('safe-free-motion', {'plan-free-motion': 1, 'trajcollision': 0},
                          from_fn(get_free_motion_synth(robot, movable, teleport))),
        StreamSynthesizer('safe-holding-motion', {'plan-holding-motion': 1, 'trajcollision': 0},
                          from_fn(get_holding_motion_synth(robot, movable, teleport))),
    ] if USE_SYNTHESIZERS else []
    print('Init:', init)
    print('Goal:', goal)
    print('Streams:', stream_map.keys())
    print('Synthesizers:', stream_map.keys())
    print(names)

    pr = cProfile.Profile()
    pr.enable()
    solution = solve_focused(pddlstream_problem, synthesizers=synthesizers, max_cost=INF, verbose=False)
    print_solution(solution)
    plan, cost, evaluations = solution
    pr.disable()
    # pstats.Stats(pr).sort_stats('tottime').print_stats(10)
    if plan is None:
        return

    if (not display) or (plan is None):
        disconnect()
        return

    if not viewer: # TODO: how to reenable the viewer
        disconnect()
        connect(use_gui=True)
        load_world()
    else:
        saved_world.restore()

    command = postprocess_plan(plan)
    # user_input('Execute?')
    wait_for_duration(2)
    if simulate:
        command.control()
    else:
        #command.step()
        command.refine(num_steps=50).execute(time_step=0.001)

    #wait_for_interrupt()
    user_input('Finish?')
    disconnect()

if __name__ == '__main__':
    main()