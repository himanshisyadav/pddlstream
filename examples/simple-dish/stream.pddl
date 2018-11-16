; everything written here, should have a corresponding function!
(define (stream kitchen2d)
	
	(:stream sample-motion
		:inputs (?gripper ?pose ?pose2)
		:domain (and (IsGripper ?gripper) (IsPose ?gripper ?pose) (IsPose ?gripper ?pose2))
		:outputs (?control)
		:certified (and (Motion ?gripper ?pose ?pose2 ?control) (IsControl ?control))
	)

	(:stream sample-scoop
		:inputs (?gripper ?cup ?pose3)
		:domain (and (IsGripper ?gripper)
					(IsCup ?cup) (IsPose ?cup ?pose3))
		:outputs (?pose ?pose2 ?control)
		:certified (and (CanScoop ?gripper ?pose ?pose2 ?cup ?pose3 ?control)
						(IsPose ?gripper ?pose) (IsPose ?gripper ?pose2)
						)
	)

	(:stream sample-dump
		:inputs (?gripper ?cup ?pose2)
		:domain (and (IsGripper ?gripper)
					 (IsCup ?cup)
					(IsPose ?cup ?pose2))
		:outputs (?pose ?pose3 ?control)
		:certified (and (CanDump ?gripper ?pose ?pose3 ?cup ?pose2 ?control)
						(IsPose	?gripper ?pose) (IsPose ?gripper ?pose3))
	)

)
