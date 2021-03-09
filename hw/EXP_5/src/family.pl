male('george').
male('philip').
male('kydd').
male('charles').
male('mark').
male('andrew').
male('edward').
male('william').
male('harry').
male('peter').
male('james').

female('mum').
female('elizabeth').
female('margaret').
female('spencer').
female('diana').
female('anne').
female('sarah').
female('sophie').
female('zara').
female('beatrice').
female('eugenie').
female('louise').
female('charlotte').

child1('elizabeth','george').
child1('margaret','george').
child1('diana','kydd').
child1('charles','philip').
child1('anne','philip').
child1('andrew','philip').
child1('edward','philip').
child1('william','charles').
child1('harry','charles').
child1('peter','mark').
child1('zara','mark').
child1('beatrice','andrew').
child1('eugenie','andrew').
child1('louise','edward').
child1('james','edward').
child1('charlotte','william').

spouse1('george','mum').
spouse1('philip','elizabeth').
spouse1('kydd','spencer').
spouse1('charles','diana').
spouse1('mark','anne').
spouse1('andrew','sarah').
spouse1('edward','sophie').

spouse2(X,Y):- spouse1(Y,X).
spouse(X,Y):- spouse1(X,Y);spouse2(X,Y). 
child(X,Y):- child1(X,Y);(child1(X,Z),spouse(Z,Y)).

grandchild(X,Y):- child(X,Z),child(Z,Y).
greatgrandparent(X,Y):- child(Y,Z),grandchild(Z,X).
ancestor(X,Y):- child(Y,X);(child(Z,X),ancestor(Z,Y)).
sibling(X,Y):- child(X,Z),child(Y,Z),X\=Y.
brother(X,Y):- sibling(X,Y),male(X).
sister(X,Y):- sibling(X,Y),female(X).
daughter(X,Y):- female(X),child(X,Y).
son(X,Y):- male(X),child(X,Y).
brotherinlaw1(X,Y):- brother(X,Y);(sister(Z,Y),spouse(X,Z)).
brotherinlaw(X,Y):- brotherinlaw1(X,Y);spouse(Y,Z),brotherinlaw1(X,Z).
sisterinlaw1(X,Y):- sister(X,Y);(brother(Z,Y),spouse(X,Z)).
sisterinlaw(X,Y):- sisterinlaw1(X,Y);spouse(Y,Z),sisterinlaw1(X,Z).
%此处distance只能找到同一个祖先情况下的distance，没必要使用
%distance1(X,Y,N):- child(Z,Y),N1 is N-1,distance1(X,Z,N1).
%distance1(X,Y,0):- X=Y;sisterinlaw(X,Y);brotherinlaw(X,Y);spouse(X,Y).
%distance(X,Y,N):- distance1(X,Y,N);distance1(Y,X,N).
mthCousinNremoved(X,Y,0,0):- sibling(X,Y).
mthCousinNremoved(X,Y,M,0):- child(X,I),child(Y,J),M1 is M-1,mthCousinNremoved(I,J,M1,0).
mthCousinNremoved(X,Y,M,N):- child(Y,Z),N1 is N-1,mthCousinNremoved(X,Z,M,N1).
firstcousin(X,Y):- mthCousinNremoved(X,Y,1,0).
aunt(X,Y):- female(X),child(Z,X),firstcousin(Z,Y).
uncle(X,Y):- male(X),child(Z,X),firstcousin(Z,Y).