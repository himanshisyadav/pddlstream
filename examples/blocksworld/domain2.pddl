(define (domain blocksworld)
  (:requirements :strips :equality)
  (:predicates (clear ?x)

               (is-cup ?c)
               (is-vanilla ?x)
               (is-straw ?x)
               (is-nuts ?x)

               (first-scoop ?c ?x)
               (second-scoop ?c ?x)
               (third-scoop ?c ?x)

               (AddedOne ?c)
               (AddedTwo ?c)

               (Order ?ob ?a ?b ?c)
               (DirtyVanilla)
               (DirtyStraw)
               (DirtyNuts)
  )

  (:action addFirstScoopVanilla
    :parameters  (?ob ?c)
    :precondition (and (is-cup ?c) (is-vanilla ?ob) (clear ?c)  (not (DirtyStraw)) (not (DirtyNuts)) )
    :effect (and (first-scoop ?c ?ob) (not (clear ?c)) (DirtyVanilla) (AddedOne ?c) )
  )

  (:action addSecondScoopVanilla
    :parameters  (?ob ?c)
    :precondition (and (is-cup ?c) (is-vanilla ?ob) (not (clear ?c))  (not (DirtyStraw)) (not (DirtyNuts)) (AddedOne ?c)  ) 
    :effect (and (second-scoop ?c ?ob) (DirtyVanilla) (AddedTwo ?c) )
  )

  (:action addThirdScoopVanilla
    :parameters  (?ob ?c)
    :precondition (and (is-cup ?c) (is-vanilla ?ob) (not (clear ?c))  (not (DirtyStraw)) (not (DirtyNuts))  (AddedTwo ?c) ) 
    :effect (and (third-scoop ?c ?ob) (DirtyVanilla) )
  )

  (:action addFirstScoopStraw
    :parameters  (?ob ?c)
    :precondition (and (is-cup ?c) (is-straw ?ob) (clear ?c)  (not (DirtyVanilla)) (not (DirtyNuts)) )
    :effect (and (first-scoop ?c ?ob) (not (clear ?c)) (DirtyStraw) (AddedOne ?c) )
  )

  (:action addSecondScoopStraw
    :parameters  (?ob ?c)
    :precondition (and (is-cup ?c) (is-straw ?ob) (not (clear ?c)) (not (DirtyVanilla)) (not (DirtyNuts)) (AddedOne ?c)  ) 
    :effect (and (second-scoop ?c ?ob) (DirtyStraw) (AddedTwo ?c) )
  )

  (:action addThirdScoopStraw
    :parameters  (?ob ?c)
    :precondition (and (is-cup ?c) (is-straw ?ob) (not (clear ?c)) (not (DirtyVanilla)) (not (DirtyNuts)) (AddedTwo ?c)  ) 
    :effect (and (third-scoop ?c ?ob)(DirtyStraw) )
  )

  (:action addFirstScoopNuts
    :parameters  (?ob ?c)
    :precondition (and (is-cup ?c) (is-nuts ?ob) (clear ?c)  (not (DirtyStraw)) (not (DirtyVanilla))  )
    :effect (and (first-scoop ?c ?ob) (not (clear ?c)) (DirtyNuts) (AddedOne ?c) )
  )

  (:action addSecondScoopNuts
    :parameters  (?ob ?c)
    :precondition (and (is-cup ?c) (is-nuts ?ob) (not (clear ?c))  (not (DirtyStraw)) (not (DirtyVanilla))  (AddedOne ?c)  ) 
    :effect (and (second-scoop ?c ?ob) (DirtyNuts) (AddedTwo ?c) )
  )

  (:action addThirdScoopNuts
    :parameters  (?ob ?c)
    :precondition (and (is-cup ?c) (is-nuts ?ob) (not (clear ?c))  (not (DirtyStraw)) (not (DirtyVanilla))  (AddedTwo ?c)  ) 
    :effect (and (third-scoop ?c ?ob)(DirtyNuts) )
  )

  (:action wash
    :parameters  ()
    :precondition (or (DirtyVanilla) (DirtyNuts) (DirtyStraw) ) 
    :effect (and (not(DirtyVanilla) ) (not (DirtyNuts)) (not(DirtyStraw) ))
  )

  (:derived (Order ?ob ?a ?b ?c)
    (and  (is-cup ?ob) (first-scoop ?ob ?a)  (second-scoop ?ob ?b)  (third-scoop ?ob ?c)  )
  )
)