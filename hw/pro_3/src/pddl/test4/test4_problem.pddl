(define (problem stack-blocks-stacked-ba-from-table1-to-stacked-ab-table3-onepilepertable)
    (:domain blocksworld)
	(:objects 
		a b t1 t2 t3
	)
  (:init 
		(block a)
		(block b) 
		(table t1) 
		(table t2) 
		(table t3)
        (on a t1) 
		(on b a) 
		(clear b) 
		(clear t2) 
		(clear t3)
  )
  (:goal (and (on a b) (on b t3)))
)