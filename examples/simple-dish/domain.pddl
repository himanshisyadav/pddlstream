(define (domain kitchen2d)
    (:requirements :strips :equality)
    (:predicates
    	; Static predicates (predicates that do not change over time)
    	(IsGripper ?gripper)
    	(IsCup1 ?cup)

    	(IsPose ?cup ?pose)
    	(IsControl ?control)

    	(Motion ?gripper ?pose ?pose2 ?control)

    	(CanScoop ?gripper ?pose ?pose2 ?cup ?pose3 ?control)
    	(CanDump ?gripper ?pose ?pose3 ?cup ?pose2 ?control)

    	; Fluent predicates (predicates that change over time, which describes the state of the sytem)
    	(AtPose ?cup ?block)
    	(CanMove ?gripper)

        (DirtyVanilla)
        (DirtyStraw)
        (DirtyNuts)

    	(IsEmpty ?gripper)

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
    		(and (Motion ?gripper ?pose ?pose2 ?control)
    			(CanMove ?gripper)
    			(AtPose ?gripper ?pose) (not (Unsafe ?control)))
    	:effect
    		(and (AtPose ?gripper ?pose2)
    			(not (AtPose ?gripper ?pose))
    			(not (CanMove ?gripper)) ;This is to avoid double move
    			(increase (total-cost) 1))
    )

    (:action scoopvanilla
    	:parameters (?gripper ?pose ?pose2 ?cup ?pose3 ?control) 
    	:precondition
    		(and (CanScoop ?gripper ?pose ?pose2 ?cup ?pose3 ?control)
    			(AtPose ?gripper ?pose) (IsEmpty ?gripper)
    			(AtPose ?cup ?pose3) (HasVanilla ?cup) (not (DirtyVanilla)))
    	:effect
    		(and (AtPose ?gripper ?pose2) (HasVanilla ?gripper) (DirtyVanilla)
    			(CanMove ?gripper) (not (IsEmpty ?gripper))
    			(not (AtPose ?gripper ?pose)) (increase (total-cost) 1))
    )

    (:action scoopstraw
        :parameters (?gripper ?pose ?pose2 ?cup ?pose3 ?control)
        :precondition
            (and (CanScoop ?gripper ?pose ?pose2 ?cup ?pose3 ?control)
                (AtPose ?gripper ?pose) (IsEmpty ?gripper)
                (AtPose ?cup ?pose3) (HasStraw ?cup) (not (DirtyStraw)))
        :effect
            (and (AtPose ?gripper ?pose2) (HasStraw ?gripper) (DirtyStraw)
                (CanMove ?gripper) (not (IsEmpty ?gripper))
                (not (AtPose ?gripper ?pose)) (increase (total-cost) 1))
    )

    (:action scoopnuts
        :parameters (?gripper ?pose ?pose2 ?cup ?pose3 ?control)
        :precondition
            (and (CanScoop ?gripper ?pose ?pose2 ?cup ?pose3 ?control)
                (AtPose ?gripper ?pose) (IsEmpty ?gripper)
                (AtPose ?cup ?pose3) (HasNuts ?cup) (not (DirtyNuts)) )
        :effect
            (and (AtPose ?gripper ?pose2) (HasNuts ?gripper) (DirtyNuts)
                (CanMove ?gripper) (not (IsEmpty ?gripper))
                (not (AtPose ?gripper ?pose)) (increase (total-cost) 1))
    )

  (:action wash
    :parameters (?o ?p ?g ?q ?t)
    :precondition (and (Kin ?o ?p ?g ?q ?t)
                       (AtPose ?o ?p) (HandEmpty) (Wash ?o) (AtConf ?q) (not (UnsafeTraj ?t)) (or (VanillaDirty) (StrawDirty)))
    :effect (and (CanMove)
                 (not (AtPose ?o ?p)) (not (VanillaDirty)) (not (StrawDirty)) )
  )
  
    (:action dumpvanilla1
    	:parameters (?gripper ?pose ?pose3 ?cup ?pose2 ?control)
    	:precondition
    		(and (CanDump ?gripper ?pose ?pose3 ?cup ?pose2 ?control)
    			(AtPose ?gripper ?pose) (not (IsEmpty ?gripper))
    			(AtPose ?cup ?pose2) (HasVanilla ?gripper))
    	:effect
    		(and (HasVanilla ?cup) (CanMove ?gripper)
    			(not (HasVanilla ?gripper)) (IsEmpty ?gripper)
    			(not (AtPose ?gripper ?pose)) (AtPose ?gripper ?pose3)
    			(increase (total-cost) 1))
    )


   (:action dumpstraw1
        :parameters (?gripper ?pose ?pose3 ?cup ?pose2 ?control)
        :precondition
            (and (CanDump ?gripper ?pose ?pose3 ?cup ?pose2 ?control)
                (AtPose ?gripper ?pose) (not (IsEmpty ?gripper))
                (AtPose ?cup ?pose2) (HasStraw ?gripper))
        :effect
            (and (HasStraw ?cup) (CanMove ?gripper)
                (not (HasStraw ?gripper)) (IsEmpty ?gripper)
                (not (AtPose ?gripper ?pose)) (AtPose ?gripper ?pose3)
                (increase (total-cost) 1))
    )

   (:action dumpnuts1
        :parameters (?gripper ?pose ?pose3 ?cup ?pose2 ?control)
        :precondition
            (and (CanDump ?gripper ?pose ?pose3 ?cup ?pose2 ?control)
                (AtPose ?gripper ?pose) (not (IsEmpty ?gripper))
                (AtPose ?cup ?pose2) (HasNuts ?gripper))
        :effect
            (and (HasNuts ?cup) (CanMove ?gripper)
                (not (HasNuts ?gripper)) (IsEmpty ?gripper)
                (not (AtPose ?gripper ?pose)) (AtPose ?gripper ?pose3)
                (increase (total-cost) 1))
    )

    (:derived (Unsafe ?control)
        (exists (?cup ?pose) (and (Collision ?control ?cup ?pose) (AtPose ?cup ?pose)))
    )

)

