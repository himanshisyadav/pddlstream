(define (domain blocksworld)
  (:requirements :strips :equality)
  (:predicates (clear ?x)

               (is-cup ?c)
               (is-vanilla ?x)
               (is-straw ?x)

               (first-scoop ?x)
               (second-scoop ?x)
               (third-scoop ?x)

               (Order ?ob ?a ?b ?c)
               (DirtyVanilla)
               (DirtyStraw)
  )

  (:action addFirstScoopVanilla
    :parameters  (?ob ?c)
    :precondition (and (is-cup ?c) (is-vanilla ?ob) (clear ?c) (not (DirtyStraw)) )
    :effect (and (first-scoop ?ob) (not (clear ?c)) (DirtyVanilla) )
  )

  (:action addSecondScoopVanilla
    :parameters  (?ob ?c)
    :precondition (and (is-cup ?c) (is-vanilla ?ob) (not (clear ?c)) (not (DirtyStraw)) ) 
    :effect (and (second-scoop ?ob) (DirtyVanilla))
  )

  (:action addThirdScoopVanilla
    :parameters  (?ob ?c)
    :precondition (and (is-cup ?c) (is-vanilla ?ob) (not (clear ?c)) (not (DirtyStraw)) ) 
    :effect (and (third-scoop ?ob)(DirtyVanilla))
  )

  (:action addFirstScoopStraw
    :parameters  (?ob ?c)
    :precondition (and (is-cup ?c) (is-straw ?ob) (clear ?c) (not (DirtyVanilla)) )
    :effect (and (first-scoop ?ob) (not (clear ?c)) (DirtyStraw) )
  )

  (:action addSecondScoopStraw
    :parameters  (?ob ?c)
    :precondition (and (is-cup ?c) (is-straw ?ob) (not (clear ?c)) (not (DirtyVanilla)) ) 
    :effect (and (second-scoop ?ob) (DirtyStraw))
  )

  (:action addThirdScoopStraw
    :parameters  (?ob ?c)
    :precondition (and (is-cup ?c) (is-straw ?ob) (not (clear ?c)) (not (DirtyVanilla)) ) 
    :effect (and (third-scoop ?ob)(DirtyStraw))
  )

  (:action wash
    :parameters  ()
    :precondition (or (DirtyVanilla) (DirtyStraw) ) 
    :effect (and (not(DirtyVanilla) ) (not(DirtyStraw) ))
  )

  (:derived (Order ?ob ?a ?b ?c)
    (and  (is-cup ?ob) (first-scoop ?a)  (second-scoop ?b)  (third-scoop ?c)  )
  )


)