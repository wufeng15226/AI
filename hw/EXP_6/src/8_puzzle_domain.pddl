(define (domain puzzle)
(:requirements :strips :typing :equality)
(:types num,local)
(:predicates (empty ?x - local)
            (at ?x - num ?y - local)
            (nexto ?x - local ?y - local)
)

(:action slide
            :parameters (?z - num ?x - local ?y - local )
            :precondition (and (empty ?y) (at ?z ?x) (nexto ?x ?y)
            )
            :effect (and (at ?z ?y) (empty ?x) (not (at ?z ?x)) (not (empty ?y))
            )
)

)