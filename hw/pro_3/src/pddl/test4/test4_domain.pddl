(define (domain blocksworld)
  (:requirements :strips)
  (:action move2
     :parameters (?b ?x ?y)
     :precondition (and (block ?b) (table ?x) (table ?y) (on ?b ?x) (clear ?b) (clear ?y))
     :effect (and (not (on ?b ?x)) (on ?b ?y) (clear ?x) (not (clear ?y)))
     )
  (:action stack
     :parameters (?a ?x ?b ?y)
     :precondition (and (block ?a) (block ?b) (table ?x) (table ?y) (clear ?a) (clear ?b) (on ?a ?x) (on ?b ?y))
     :effect (and (on ?a ?b) (not (on ?a ?x)) (not (clear ?b)) (clear ?x))
     )
  (:action unstack
     :parameters (?a ?b ?x ?y)
     :precondition (and (block ?a) (block ?b) (table ?x) (table ?y) (on ?b ?x) (on ?a ?b) (clear ?a) (clear ?y))
     :effect (and (on ?a ?y) (not (on ?a ?b)) (clear ?b) (clear ?a) (not (clear ?y)))
     )
)