#!/usr/bin/env python

from __future__ import print_function

import cProfile
import pstats
import argparse

from examples.pybullet.utils.pybullet_tools.kuka_primitives import BodyPose, BodyConf, Command, get_grasp_gen, \
    get_stable_gen, get_ik_fn, get_free_motion_gen, \
    get_holding_motion_gen, get_movable_collision_test
from examples.pybullet.utils.pybullet_tools.utils import WorldSaver, connect, dump_world, get_pose, set_pose, Pose, \
    Point, set_default_camera, stable_z, \
    BLOCK_URDF, get_configuration, SINK_URDF, STOVE_URDF, load_model, is_placement, get_body_name, \
    disconnect, DRAKE_IIWA_URDF, get_bodies, user_input, HideOutput
    
from pddlstream.algorithms.focused import solve_focused
from pddlstream.language.generator import from_gen_fn, from_fn, empty_gen
from pddlstream.language.synthesizer import StreamSynthesizer
from pddlstream.utils import print_solution, read, INF, get_file_path, find_unique

import random

USE_SYNTHESIZERS = False

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
    domain_pddl = read(get_file_path(__file__, 'domain2.pddl'))
    stream_pddl = read(get_file_path(__file__, 'stream2.pddl'))
    constant_map = {}

    print('Robot:', robot)
    conf = BodyConf(robot, get_configuration(robot))
    init = [('CanMove',),
            ('Conf', conf),
            ('AtConf', conf),
            ('HandEmpty',),
            ('Cleaned',)]

    fixed = get_fixed(robot, movable)

    # movable_bodies = [tub_straw, tub_vanilla, bowl1, bowl2, bowl3, wash, scoop_vanilla1, scoop_vanilla2, scoop_vanilla3, scoop_straw1, scoop_straw2, scoop_straw3]
    tub_straw = movable[0]
    tub_vanilla = movable[1]
    bowl1 = movable[2]
    bowl2 = movable[3]

    wash = movable[4]

    vanilla_scoop1 = movable[5]
    vanilla_scoop2 = movable[6]

    straw_scoop1 = movable[7]
    straw_scoop2 = movable[8]

    print('Movable:', movable)
    print('Fixed:', fixed)
    for body in movable:
        pose = BodyPose(body, get_pose(body))
        init += [('Graspable', body),
                 ('Pose', body, pose),
                 ('AtPose', body, pose)]
        for surface in movable:
            if body != surface:
                # init += [('Stackable', body, surface)]
                if is_placement(body, surface):
                    init += [('Supported', body, pose, surface)]

    init += [('isEmpty1',)]
    init += [('isEmpty2',)]
    init += [('Bowl1', bowl1)]
    init += [('Bowl2', bowl2)]

    init += [('VanillaScoop', vanilla_scoop1)]
    init += [('VanillaScoop', vanilla_scoop2)]
    init += [('StrawScoop', straw_scoop1)]
    init += [('StrawScoop', straw_scoop2)]

    init += [('Wash', wash)]

    ss = [straw_scoop1, straw_scoop2]
    vs = [vanilla_scoop1, vanilla_scoop2]

    for a in ss: 
        init += [('Stackable', a, bowl1)]
        init += [('Stackable', a, bowl2)]
    for a in vs: 
        init += [('Stackable', a, bowl1)]
        init += [('Stackable', a, bowl2)]
    for a in ss: 
        for b in vs: 
            init += [('Stackable', a, b)]
            init += [('Stackable', b, a)]

    random.shuffle(ss)
    random.shuffle(vs)

    goal = ('and',
            ('AtConf', conf),

            ('First1', ss[0], bowl1),
            ('Second1', vs[0], ss[0]),

            ('First2', ss[1], bowl2),
            ('Second2', vs[1], ss[1]),

            # ('First3', vs[2], bowl3),
            # ('Second3', vs[2], ss[2]),


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
        floor = load_model('models/short_floor.urdf')
        tub_straw = load_model('models/tub_straw.urdf', fixed_base=False )
        tub_vanilla = load_model('models/tub_vanilla.urdf', fixed_base=False )
        wash = load_model('models/tub_wash.urdf', fixed_base=False)

        bowl1 = load_model('models/bowl.urdf', fixed_base=False)
        bowl2 = load_model('models/bowl.urdf', fixed_base=False)

        scoop_vanilla1 = load_model('models/vanilla_scoop.urdf', fixed_base=False)
        scoop_straw1 = load_model('models/straw_scoop.urdf', fixed_base=False)
        scoop_vanilla2 = load_model('models/vanilla_scoop.urdf', fixed_base=False)
        scoop_straw2 = load_model('models/straw_scoop.urdf', fixed_base=False)

    body_names = {
        tub_straw: 'tub_straw',
        tub_vanilla: 'tub_vanilla',
        scoop_vanilla1: 'scoop_vanilla1',
        scoop_vanilla2: 'scoop_vanilla2',
        scoop_straw1: 'scoop_straw1',
        scoop_straw2: 'scoop_straw2',
        bowl1: 'bowl1',
        bowl2: 'bowl2',
        wash: 'wash',
    }
    
    movable_bodies = [tub_straw, tub_vanilla, bowl1, bowl2, wash, scoop_vanilla1, scoop_vanilla2, scoop_straw1, scoop_straw2]
    set_pose(tub_straw, Pose(Point(x=0.5, y=-0.5, z=-0.1)))
    set_pose(tub_vanilla, Pose(Point(x=+0.5, y=+0.0, z=-0.1)))

    set_pose(scoop_straw1, Pose(Point(x=0.5, y=-0.5, z=stable_z(scoop_straw1, tub_straw))))
    set_pose(scoop_vanilla1, Pose(Point(x=+0.5, y=+0.0, z=stable_z(scoop_vanilla1, tub_vanilla))))
    set_pose(scoop_straw2, Pose(Point(x=0.65, y=-0.5, z=stable_z(scoop_straw2, tub_straw))))
    set_pose(scoop_vanilla2, Pose(Point(x=+0.65, y=+0.0, z=stable_z(scoop_vanilla2, tub_vanilla))))

    set_pose(wash, Pose(Point(x=-0.5, y=+0.0, z=-0.1)))
    set_pose(bowl1, Pose(Point(x=-0.4, y=+0.5, z=0.0)))
    set_pose(bowl2, Pose(Point(x=-0.0, y=+0.5, z=0.0)))
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
    solution = solve_focused(pddlstream_problem, synthesizers=synthesizers, max_cost=INF)

    print_solution(solution)
    plan, cost, evaluations = solution
    pr.disable()
    pstats.Stats(pr).sort_stats('tottime').print_stats(10)
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
    if simulate:
        command.control()
    else:
        #command.step()
        command.refine(num_steps=10).execute(time_step=0.001)

    #wait_for_interrupt()
    user_input('Finish?')
    disconnect()

if __name__ == '__main__':
    main()