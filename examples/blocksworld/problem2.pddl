(define (problem pb2)
   (:domain blocksworld)
   (:objects a b cup)
   (:init
     (is-cup cup)
     (clear cup)
     (is-vanilla a)
     (is-straw b)
   )
   (:goal ( and 
   				(Order cup b a b) 
   		  )
   )
)