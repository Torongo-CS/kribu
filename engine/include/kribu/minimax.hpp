/**
 * @file minimax.hpp
 * @brief Minimax search algorithm with alpha-beta pruning for Sholo Guti.
 */

#pragma once

#include <algorithm>
#include <array>

#include "board.hpp"
#include "rules.hpp"
#include "types.hpp"

namespace kribu::sholoGuti {

/**
 * @brief Infinity value used as bounds in alpha-beta pruning.
 */
constexpr i32 INFINITY_VAL = 1000000;

/**
 * @struct MinimaxResult
 * @brief Represents the output of a minimax search, containing the best score and the best move ID.
 */
struct MinimaxResult {
  /**
   * @brief The evaluation score of the best move found.
   */
  i32 score = 0;

  /**
   * @brief The move ID of the best move found.
   */
  int moveId = -1;
};

/**
 * @brief Computes a static heuristic evaluation of the board from the active player's perspective.
 * @param state The board state to evaluate.
 * @return The static evaluation score. Positive values favor the active player.
 */
[[nodiscard]] inline i32 evaluate_board(const boardState& state) noexcept {
  return 100 * (piece_count(state.me) - piece_count(state.opp));
}

/**
 * @struct OrderedMoveList
 * @brief Stores an ordered array of move IDs and the count of elements.
 */
struct OrderedMoveList {
  /**
   * @brief Array buffer storing the ordered move IDs.
   */
  std::array<i16, MAX_MOVES_PER_STATE> moves{};

  /**
   * @brief The number of elements currently stored in the list.
   */
  int count = 0;
};

/**
 * @brief Orders a MoveList to prioritize capture moves for optimal alpha-beta cutoffs.
 * @param moves The original MoveList to order.
 * @return OrderedMoveList containing capture moves first, then simple/end-chain moves.
 */
[[nodiscard]] inline OrderedMoveList order_moves(const MoveList& moves) noexcept {
  OrderedMoveList ordered;
  for (int i = 0; i < moves.count; ++i) {
    if (is_capture_move(moves.moves[i])) {
      ordered.moves[ordered.count++] = moves.moves[i];
    }
  }
  for (int i = 0; i < moves.count; ++i) {
    if (!is_capture_move(moves.moves[i])) {
      ordered.moves[ordered.count++] = moves.moves[i];
    }
  }
  return ordered;
}

/**
 * @brief Executes a minimax search with alpha-beta pruning.
 * @param state The current board state to search from.
 * @param depth The maximum search depth remaining.
 * @param alpha The lower bound score of the search window.
 * @param beta The upper bound score of the search window.
 * @return A MinimaxResult containing the best score and best move ID.
 */
[[nodiscard]] inline MinimaxResult minimax(const boardState& state, int depth, i32 alpha, i32 beta) noexcept {
  if (piece_count(state.opp) == 0) {
    return MinimaxResult{.score = INFINITY_VAL + depth, .moveId = -1};
  }
  if (piece_count(state.me) == 0) {
    return MinimaxResult{.score = -INFINITY_VAL - depth, .moveId = -1};
  }

  if (depth <= 0) {
    return MinimaxResult{.score = evaluate_board(state), .moveId = -1};
  }

  MoveList moves = all_possible_moves(state);
  if (moves.empty()) {
    return MinimaxResult{.score = -INFINITY_VAL - depth, .moveId = -1};
  }

  const OrderedMoveList ordered = order_moves(moves);
  int bestMoveId = -1;
  i32 bestScore = -INFINITY_VAL - 10000;

  for (int i = 0; i < ordered.count; ++i) {
    const int moveId = ordered.moves[i];
    const boardState nextState = apply_move(state, moveId);

    i32 score = 0;
    if (nextState.activeCaptureIdx == -1) {
      const boardState flippedState = flip_board(nextState);
      const MinimaxResult res = minimax(flippedState, depth - 1, -beta, -alpha);
      score = -res.score;
    } else {
      const MinimaxResult res = minimax(nextState, depth - 1, alpha, beta);
      score = res.score;
    }

    if (score > bestScore) {
      bestScore = score;
      bestMoveId = moveId;
    }

    alpha = std::max(alpha, bestScore);
    if (alpha >= beta) {
      break;
    }
  }

  return MinimaxResult{.score = bestScore, .moveId = bestMoveId};
}

}  // namespace kribu::sholoGuti
