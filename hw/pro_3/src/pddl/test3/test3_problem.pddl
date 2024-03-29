(define (problem stack-blocks-stacked-ba-from-tablex-to-stacked-ab-tabley)
  (:domain blocksworld)
  (:objects
    a b - block
    x y - table
  )
  (:init
		(block a)
		(block b)
		(table x)
		(table y)
        (on a x)
		(on b a)
		(clear b)
  )
  (:goal (and (on b y) (on a b) (clear a) (not (clear b))))
)