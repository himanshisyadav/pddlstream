(define (domain blocksworld)
    (:requirements :strips :equality)
    (:predicates
      ; Static predicates (predicates that do not change over time)
      (IsCup1 ?cup)

      (DirtyVanilla)
      (DirtyStraw)
      (DirtyNuts)

      (GripperEmpty)
      (HasVanilla)
      (HasStraw)
      (HasNuts)

      (On ?cup ?block)
    )

    (:action scoopvanilla
      :parameters () 
      :precondition
        (and (GripperEmpty) (or (not (DirtyStraw)) (not (DirtyNuts)) ) )  
      :effect
        (and (DirtyVanilla) (not (GripperEmpty))
         (increase (total-cost) 1))
    )

    (:action scoopstraw
      :parameters () 
      :precondition
        (and (GripperEmpty) (or (not (DirtyVanilla)) (not (DirtyNuts)) ) )  
      :effect
        (and (DirtyStraw) (not (GripperEmpty))
         (increase (total-cost) 1))
    )

    (:action scoopnuts
      :parameters () 
      :precondition
        (and (GripperEmpty) (or (not (DirtyVanilla)) (not (DirtyStraw)) ) )  
      :effect
        (and (DirtyNuts) (not (GripperEmpty))
         (increase (total-cost) 1))
    )

    (:action wash
      :parameters ()
      :precondition (and (HandEmpty) (or (DirtyVanilla) (DirtyStraw) (DirtyNuts)) )
      :effect (and (not (DirtyVanilla))  (not (DirtyStraw)) (not (DirtyNuts)) )
    )
  
    (:action dumpvanilla1
      :parameters (?bowl)
      :precondition
        (and (not (GripperEmpty)) (HasVanilla) )
      :effect
        (and (not (HasVanilla)) (GripperEmpty) (increase (total-cost) 1) )
    )

)

