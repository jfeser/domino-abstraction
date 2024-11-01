:- initialization(main, main).

object(domino, X) :- domino(X).
object(ball, X) :- ball_x(X).

left_of(object(K1, A), object(K2, B)) :- object(K1, A), object(K2, B), A < B.
between(A, B, C) :- left_of(A, B), left_of(B, C).
imm_left_of(A, B) :- left_of(A, B), not(between(A, _, B)).

will_move(A) :-
    A = object(domino, X),
    push(domino(X)),
    width(W), height(H),
    atom_concat('python3.11 will-tip.py ', W, Command1),
    atom_concat(Command1, ' ', Command2),
    atom_concat(Command2, H, Command),
    shell(Command, 0).

will_move(A) :-
    imm_left_of(B, A),
    height(H),
    A = object(_, X),
    B = object(_, X1),
    X - X1 =< H,
    will_move(B).

will_move(A) :-
    imm_left_of(B, A),
    B = object(ball, _),
    will_move(B).

will_beam_rotate :-
    A = object(ball, _),
    will_move(A),
    not(left_of(A, _)).

main :-
    ( will_beam_rotate -> halt(0) ; halt(1) ).
