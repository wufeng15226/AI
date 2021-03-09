(define (domain boxman_domain)
  (:requirements :strips :typing:equality
                 :universal-preconditions
                 :conditional-effects
  )
  (:types loc)
  (:predicates
    (man ?p - loc)  
    (box ?p - loc) 
    (td ?p1 - loc ?p2 - loc) 
    (lr ?p1 - loc ?p2 - loc) 
  )

	(:action move
    :parameters (?x - loc ?y - loc )
    :precondition (and (man ?x)(or (td ?x ?y)(lr ?x ?y))(not(box ?y))(not(= ?x ?y)))
    :effect (and (not(man ?x)) (man ?y))
	)

	(:action push
            :parameters (?x - loc ?y - loc ?z - loc)
            :precondition (and (man ?x) (box ?y) (not(box ?z)) (or (and (td ?x ?y) (td ?y ?z))(and (lr ?x ?y) (lr ?y ?z)))(not(= ?x ?y))(not(= ?y ?z))(not(= ?z ?x)))
            :effect (and
                      (man ?y)
                      (not(man ?x))
                      (box ?z)
                      (not(box ?y))
                    )
  )
)