import chess

from typing import Iterator, Optional
from heckmeckengine.engine.annotated_move import AnnotatedMove


class HeckmeckBoard(chess.Board):
    def __init__(
        self: chess.BoardT,
        fen: Optional[str] = chess.STARTING_FEN,
        *,
        chess960: bool = False
    ) -> None:
        super().__init__(fen, chess960=chess960)
        self.killer_moves = {}

        self._QUITE_MOVE_PIECE_ORDER = [
            chess.QUEEN,
            chess.ROOK,
            chess.BISHOP,
            chess.KNIGHT,
            chess.PAWN,
            chess.KING,
        ]

        self._LVA = [
            chess.PAWN,
            chess.KNIGHT,
            chess.BISHOP,
            chess.ROOK,
            chess.QUEEN,
            chess.KING,
        ]
        self._MVV = [
            chess.QUEEN,
            chess.ROOK,
            chess.BISHOP,
            chess.KNIGHT,
            chess.PAWN,
        ]

    def generate_legal_moves(
        self,
        from_mask: chess.Bitboard = chess.BB_ALL,
        to_mask: chess.Bitboard = chess.BB_ALL,
        pv_move: AnnotatedMove = chess.Move.null(),
        generate_null_move=False,
    ) -> Iterator[AnnotatedMove]:
        if self.is_variant_end():
            return

        king_mask = self.kings & self.occupied_co[self.turn]
        if king_mask:
            king = chess.msb(king_mask)
            blockers = self._slider_blockers(king)
            checkers = self.attackers_mask(not self.turn, king)
            if checkers:
                for move in self._generate_evasions(king, checkers, from_mask, to_mask):
                    if self._is_safe(king, blockers, move):
                        yield move
            else:
                for move in self.generate_pseudo_legal_moves(
                    from_mask,
                    to_mask,
                    pv_move,
                    generate_null_move,
                ):
                    if self._is_safe(king, blockers, move):
                        yield move
        else:
            yield from self.generate_pseudo_legal_moves(
                from_mask,
                to_mask,
                pv_move,
                generate_null_move,
            )

    def generate_pseudo_legal_moves(
        self,
        from_mask: chess.Bitboard = chess.BB_ALL,
        to_mask: chess.Bitboard = chess.BB_ALL,
        pv_move: AnnotatedMove = chess.Move.null(),
        generate_null_move=False,
    ) -> Iterator[AnnotatedMove]:
        # PV move
        if pv_move:
            yield pv_move
            searched_moves = {pv_move}
        else:
            searched_moves = set()

        # Null move
        if generate_null_move:
            move = chess.Move.null()
            move.__class__ = AnnotatedMove
            yield move

        #
        # Queen promotions which are captures
        pawns = self.pawns & self.occupied_co[self.turn] & from_mask
        for from_square in chess.scan_reversed(pawns):
            targets = (
                chess.BB_PAWN_ATTACKS[self.turn][from_square]
                & self.occupied_co[not self.turn]
                & (to_mask & (chess.BB_RANK_1 | chess.BB_RANK_8))
            )

            for to_square in chess.scan_reversed(targets):
                move = AnnotatedMove(from_square, to_square, chess.QUEEN)
                if move not in searched_moves:
                    yield move

        # Queen promotions
        for move in self._generate_promotions_without_capture(
            from_mask=from_mask,
            to_mask=to_mask,
            promotion_piece_types=(chess.QUEEN,),
        ):
            if move not in searched_moves:
                yield move

        # Pawn captures
        pawns = self.pawns & self.occupied_co[self.turn] & from_mask
        for from_square in chess.scan_reversed(pawns):
            for piece_type_defender in self._MVV:
                targets = (
                    chess.BB_PAWN_ATTACKS[self.turn][from_square]
                    & self.pieces_mask(piece_type_defender, not self.turn)
                    & (to_mask & ~(chess.BB_RANK_1 | chess.BB_RANK_8))
                )

                for to_square in chess.scan_reversed(targets):
                    move = AnnotatedMove(from_square, to_square)
                    if move not in searched_moves:
                        yield move

        # En passant
        if self.ep_square:
            for move in self.generate_pseudo_legal_ep(from_mask, to_mask):
                if move not in searched_moves:
                    yield move

        # Killer Moves

        # Castling
        if from_mask & self.kings:
            for move in self.generate_castling_moves(from_mask, to_mask):
                if move not in searched_moves:
                    yield move

        # Captures
        for piece_type_attacker in self._LVA[1:]:
            attacker_squares = (
                self.pieces_mask(piece_type_attacker, self.turn) & from_mask
            )
            for piece_type_defender in self._MVV:
                defender_squares = (
                    self.pieces_mask(piece_type_defender, not self.turn) & to_mask
                )
                for from_square in chess.scan_reversed(attacker_squares):
                    for move in self._generate_move_piece(
                        from_square, to_mask & defender_squares
                    ):
                        if move not in searched_moves:
                            yield move

        # Checks

        # Quiet Moves
        for piece_type in self._QUITE_MOVE_PIECE_ORDER:
            if piece_type != chess.PAWN:
                piece_squares = self.pieces_mask(piece_type, self.turn) & from_mask
                for from_square in chess.scan_reversed(piece_squares):
                    for move in self._generate_move_piece(
                        from_square, to_mask & (~self.occupied)
                    ):
                        if move not in searched_moves:
                            yield move
            else:
                for move in self._generate_pawn_advances(
                    from_mask=from_mask,
                    to_mask=to_mask & ~(chess.BB_RANK_1 | chess.BB_RANK_8),
                ):
                    if move not in searched_moves:
                        yield move

        # Non-queen Promotions
        # Captures
        pawns = self.pawns & self.occupied_co[self.turn] & from_mask
        for from_square in chess.scan_reversed(pawns):
            targets = (
                chess.BB_PAWN_ATTACKS[self.turn][from_square]
                & self.occupied_co[not self.turn]
                & (to_mask & (chess.BB_RANK_1 | chess.BB_RANK_8))
            )
            for to_square in chess.scan_reversed(targets):
                for promotion in (
                    chess.KNIGHT,
                    chess.BISHOP,
                    chess.ROOK,
                ):
                    move = AnnotatedMove(from_square, to_square, promotion)
                    if move not in searched_moves:
                        yield move

        # Non-captures
        for move in self._generate_promotions_without_capture(
            from_mask=from_mask,
            to_mask=to_mask,
            promotion_piece_types=(chess.KNIGHT, chess.BISHOP, chess.ROOK),
        ):
            if move not in searched_moves:
                yield move

    def _generate_promotions_without_capture(
        self,
        from_mask,
        to_mask,
        promotion_piece_types,
    ):
        pawns = self.pawns & self.occupied_co[self.turn] & from_mask
        if not pawns:
            return

        if self.turn == chess.WHITE:
            single_moves = pawns << 8 & ~self.occupied
        else:
            single_moves = pawns >> 8 & ~self.occupied

        to_mask &= chess.BB_RANK_1 | chess.BB_RANK_8
        single_moves &= to_mask

        # Generate single pawn moves.
        for to_square in chess.scan_reversed(single_moves):
            from_square = to_square + (8 if self.turn == chess.BLACK else -8)

            for piece_type in promotion_piece_types:
                yield AnnotatedMove(from_square, to_square, piece_type)

    def _generate_pawn_advances(
        self, from_mask, to_mask
    ):  # Prepare pawn advance generation.
        pawns = self.pawns & self.occupied_co[self.turn] & from_mask
        if not pawns:
            return

        if self.turn == chess.WHITE:
            single_moves = pawns << 8 & ~self.occupied
            double_moves = (
                single_moves << 8 & ~self.occupied & (chess.BB_RANK_3 | chess.BB_RANK_4)
            )
        else:
            single_moves = pawns >> 8 & ~self.occupied
            double_moves = (
                single_moves >> 8 & ~self.occupied & (chess.BB_RANK_6 | chess.BB_RANK_5)
            )

        single_moves &= to_mask
        double_moves &= to_mask

        # Generate single pawn moves.
        for to_square in chess.scan_reversed(single_moves):
            from_square = to_square + (8 if self.turn == chess.BLACK else -8)

            if chess.square_rank(to_square) in [0, 7]:  # Promotions
                yield AnnotatedMove(from_square, to_square, chess.QUEEN)
                yield AnnotatedMove(from_square, to_square, chess.ROOK)
                yield AnnotatedMove(from_square, to_square, chess.BISHOP)
                yield AnnotatedMove(from_square, to_square, chess.KNIGHT)
            else:
                yield AnnotatedMove(from_square, to_square)

        # Generate double pawn moves.
        for to_square in chess.scan_reversed(double_moves):
            from_square = to_square + (16 if self.turn == chess.BLACK else -16)
            yield AnnotatedMove(from_square, to_square)

    def _generate_move_piece(self, from_square, to_mask):
        to_squares = self.attacks_mask(from_square) & to_mask
        for to_square in chess.scan_reversed(to_squares):
            yield AnnotatedMove(from_square, to_square)

    def add_killer_move(self, move: AnnotatedMove):
        ply = self.board.ply()
        if ply not in self.killer_moves:
            self.killer_moves[ply] = (None, None)

        new_killer_moves = (move, self.killer_moves[ply][0])
        self.killer_moves[ply] = new_killer_moves


if __name__ == "__main__":
    board = HeckmeckBoard()
    moves = board.generate_pseudo_legal_moves()
    print(len([m for m in moves]))
