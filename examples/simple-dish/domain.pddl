(define (domain kitchen2d)
    (:requirements :strips :equality)
    (:predicates
    	; Static predicates (predicates that do not change over time)
    	(IsGripper ?gripper) ; gripper is the robot? 
    	(IsCup ?cup)
    	(IsSpoon ?kettle)
    	(IsBlock ?cup)	;why is cup a block
    	(IsPourable ?cup)

    	(IsPose ?cup ?pose) ;only cup has pose?
    	(IsGrasp ?cup ?grasp) ; only cup can be grasped? 
    	(IsControl ?control) ; what does this mean? 

    	(CanGrasp ?gripper ?pose ?cup ?pose2 ?grasp ?control)
    	(BelowFaucet ?gripper ?pose ?cup ?grasp)
    	(CanPour ?gripper ?pose ?cup ?grasp ?kettle ?pose2 ?control)
    	(Motion ?gripper ?pose ?pose2 ?control) ; what does this mean? 
    	(MotionH ?gripper ?pose ?cup ?grasp ?pose2 ?control)

    	(CanScoop ?gripper ?pose ?pose2 ?spoon ?grasp ?kettle ?pose3 ?control)
    	(CanDump ?gripper ?pose ?pose3 ?spoon ?grasp ?kettle ?pose2 ?control)
    	(CanPush ?gripper ?pose ?pose2 ?cup ?pose3 ?pose4 ?control)

    	(BlockSupport ?cup ?pose ?block ?pose2)
    	(Clear ?block)
    	(TableSupport ?pose)

    	; Fluent predicates (predicates that change over time, which describes the state of the sytem)
    	(AtPose ?cup ?block)
    	(Grasped ?cup ?grasp)
    	(Empty ?gripper)
    	(CanMove ?gripper)
    	(HasCoffee ?cup)
    	(HasVanilla ?cup)
    	(HasCream ?cup)
    	(Scooped ?cup)

    	; Derived predicates (predicates derived from other predicates, defined with streams)
    	(Unsafe ?control)
    	(Holding ?cup)
    	(On ?cup ?block)

    	; External predicates (evaluated by external boolean functions)
    	(Collision ?control ?gripper ?pose)
    )

    (:action move
    	:parameters (?gripper ?pose ?pose2 ?control)
    	:precondition
            ; if motion is valid, gripper is empty, at start pose and safe control
    		(and (Motion ?gripper ?pose ?pose2 ?control)
    			(Empty ?gripper) (CanMove ?gripper)
    			(AtPose ?gripper ?pose) (not (Unsafe ?control)))
    	:effect
            ; change pose of gripper, prevent gripper from moving, add to cost
    		(and (AtPose ?gripper ?pose2)
    			(not (AtPose ?gripper ?pose))
    			(not (CanMove ?gripper)) ;This is to avoid double move
    			(increase (total-cost) 1))
    )
    (:action move-holding
    	:parameters (?gripper ?pose ?cup ?grasp ?pose2 ?control)
    	:precondition
    		(and (MotionH ?gripper ?pose ?cup ?grasp ?pose2 ?control)
    			(not (Empty ?gripper)) (AtPose ?gripper ?pose)
    			(Grasped ?cup ?grasp) (CanMove ?gripper) (not (Unsafe ?control)))
    	:effect
    		(and (AtPose ?gripper ?pose2) (not (AtPose ?gripper ?pose))
    			(not (CanMove ?gripper)) (increase (total-cost) 1))
    )
    (:action pick
    	:parameters	(?gripper ?pose ?cup ?pose2 ?grasp ?control)
    	:precondition
    		(and (CanGrasp ?gripper ?pose ?cup ?pose2 ?grasp ?control)
    			(AtPose ?gripper ?pose) (AtPose ?cup ?pose2)
    			(Empty ?gripper) (TableSupport ?pose2))
    	:effect
    		(and (Grasped ?cup ?grasp) (CanMove ?gripper)
    			(not (AtPose ?cup ?pose2)) (not (Empty ?gripper))
    			(increase (total-cost) 1))
    )
    (:action place
		:parameters (?gripper ?pose ?cup ?pose2 ?grasp ?control)
		:precondition
			(and (CanGrasp ?gripper ?pose ?cup ?pose2 ?grasp ?control)
				(AtPose ?gripper ?pose) (TableSupport ?pose2)
				(Grasped ?cup ?grasp) (not (Scooped ?cup)))
		:effect
			(and (AtPose ?cup ?pose2) (Empty ?gripper)
				(CanMove ?gripper) (not (Grasped ?cup ?grasp))
				(increase (total-cost) 1))
    )
    (:action fill
        ; fill with coffee
    	:parameters (?gripper ?pose ?cup ?grasp)
    	:precondition
    		(and (BelowFaucet ?gripper ?pose ?cup ?grasp)
    		    (AtPose ?gripper ?pose) (Grasped ?cup ?grasp))
    	:effect
    		(and (HasCoffee ?cup) (CanMove ?gripper)
    			(increase (total-cost) 1))
    )
    (:action pour
    	; why named kettle
        ; pour cream into kettle from cup
    	:parameters (?gripper ?pose ?cup ?grasp ?kettle ?pose2 ?control)
    	:precondition
    		(and (CanPour ?gripper ?pose ?cup ?grasp ?kettle ?pose2 ?control)
    			(AtPose ?gripper ?pose) (Grasped ?cup ?grasp)
    			(AtPose ?kettle ?pose2) (HasCream ?cup))
    	:effect
    		(and (HasCream ?kettle) (CanMove ?gripper)
    			(not (HasCream ?cup)) (increase (total-cost) 1))
    )
    (:action scoop
        ; scoop sugar into spoon if already holding spoon
    	:parameters (?gripper ?pose ?pose2 ?spoon ?grasp ?kettle ?pose3 ?control)
    	:precondition
    		(and (CanScoop ?gripper ?pose ?pose2 ?spoon ?grasp ?kettle ?pose3 ?control)
    			(AtPose ?gripper ?pose) (Grasped ?spoon ?grasp)
    			(AtPose ?kettle ?pose3) (HasVanilla ?kettle))
    	:effect
    		(and (AtPose ?gripper ?pose2) (HasVanilla ?spoon)
    			(CanMove ?gripper) (Scooped ?spoon)
    			(not (AtPose ?gripper ?pose)) (increase (total-cost) 1))
    )
    (:action dump
        ; add sugar to kettle from spoon
    	:parameters (?gripper ?pose ?pose3 ?spoon ?grasp ?kettle ?pose2 ?control)
    	:precondition
    		(and (CanDump ?gripper ?pose ?pose3 ?spoon ?grasp ?kettle ?pose2 ?control)
    			(AtPose ?gripper ?pose) (Grasped ?spoon ?grasp)
    			(AtPose ?kettle ?pose2) (HasVanilla ?spoon))
    	:effect
    		(and (HasVanilla ?kettle) (CanMove ?gripper)
    			(not (HasVanilla ?spoon)) (not (Scooped ?spoon))
    			(not (AtPose ?gripper ?pose)) (AtPose ?gripper ?pose3)
    			(increase (total-cost) 1))
    )
    ; control is unsafe when collision happens when trying to reach cup
    (:derived (Unsafe ?control)
        (exists (?cup ?pose) (and (Collision ?control ?cup ?pose) (AtPose ?cup ?pose)))
    )
    ; if a cup is being held
    (:derived (Holding ?cup)
        (exists (?grasp) (and (IsGrasp ?cup ?grasp) (Grasped ?cup ?grasp)))
    )
    ; if cup is on a block (block is a coaster?)
    (:derived (On ?cup ?block)
        (exists (?pose ?pose2) (and (BlockSupport ?cup ?pose ?block ?pose2)
                                    (AtPose ?cup ?pose) (AtPose ?block ?pose2)))
    )
)

