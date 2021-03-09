(define (domain blocks)
  (:requirements :strips :typing:equality
                 :universal-preconditions
                 :conditional-effects)
  (:types physob)
  (:predicates   
  	    (ontable ?x - physob)
        (clear ?x - physob)	
	    (on ?x ?y - physob))
		
  (:action move
             :parameters (?x ?y - physob)
             :precondition (and (clear ?x) (clear ?y) (not(= ?x ?y)))       
             :effect (and (not (clear ?y)) (on ?x ?y)
                        (forall(?z - physob)
                        (when (on ?x ?z)
                        (and (clear ?z) (not (on ?x ?z)))))
                        (when (ontable ?x)
                        (not(ontable ?x)))
                    )
  )
  (:action moveToTable
             :parameters (?x - physob)
             :precondition (and (clear ?x) (not (ontable ?x)))
             :effect (and (ontable ?x)
                        (forall (?z -physob)
                        (when (on ?x ?z)
                        (and (clear ?z) (not (on ?x ?z))))
                        )
             )
 )
)