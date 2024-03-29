(define (domain blocksworld)
  (:requirements :strips :typing)
  (:types block table)
  (:action move
     :parameters (?b - block ?t1 - table ?t2 - table)
     :precondition (and (block ?b) (table ?t1) (table ?t2) (on ?b ?t1) (not (on ?b ?t2)) (clear ?b))
     :effect (and (on ?b ?t2)) (not (on ?b ?t1)))
  (:action stack
     :parameters (?a - block ?b - block ?t1 - table)
     :precondition (and (block ?a) (block ?b) (table ?t1) (clear ?a) (clear ?b) (on ?a ?t1) (on ?b ?t1))
     :effect (and (on ?a ?b) (not (on ?a ?t1)) (not (clear ?b)))
     )
  (:action unstack
     :parameters (?a - block ?b - block ?t1 - table)
     :precondition (and (block ?a) (block ?b) (table ?t1) (on ?b ?t1) (clear ?a) (on ?a ?b))
     :effect (and (on ?a ?t1) (not (on ?a ?b)) (clear ?b))
     )
)