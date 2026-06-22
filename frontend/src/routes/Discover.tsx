import { useMemo } from "react";
import { Link } from "react-router-dom";
import {
  useDeck,
  useMatchMutation,
  useResetSkipsMutation,
  useSkipMutation,
} from "@/api/queries";
import { useAppStore } from "@/stores/useAppStore";
import SwipeCard, { type SwipeDirection } from "@/components/SwipeCard";
import { countPassedChallenges } from "@/lib/progressStats";
import type { Character } from "@/types";

export default function Discover() {
  const { data: deck = [], isLoading } = useDeck();
  const matches = useAppStore((s) => s.matches);
  const skipped = useAppStore((s) => s.skipped);
  const points = useAppStore((s) => s.points);
  const completed = useAppStore((s) => s.completed);
  const levelResults = useAppStore((s) => s.levelResults);
  const matchMutation = useMatchMutation();
  const skipMutation = useSkipMutation();
  const resetSkipsMutation = useResetSkipsMutation();
  const completedChallenges = countPassedChallenges(completed, levelResults);

  const available = useMemo<Character[]>(
    () =>
      deck.filter(
        (character) =>
          !matches.includes(character.id) && !skipped.includes(character.id),
      ),
    [deck, matches, skipped],
  );

  if (isLoading) {
    return (
      <section className="page narrow">
        <div className="card empty-state">
          <p className="lead">Đang tải bộ thẻ...</p>
        </div>
      </section>
    );
  }

  if (available.length === 0) {
    return (
      <section className="page narrow">
        <div className="card empty-state">
          <p className="kicker">Hoàn tất bộ thẻ</p>
          <h1 className="headline-lg">
            Bạn đã xem hết đợt nội dung đầu tiên.
          </h1>
          <p className="lead">
            Mở bộ sưu tập để trò chuyện, làm thử thách và hoàn thành trạng thái
            mở khóa.
          </p>
          <div className="actions-row" style={{ justifyContent: "center" }}>
            <Link className="btn primary" to="/collection">
              Xem nhân vật đã chọn
            </Link>
            <button
              className="btn ghost"
              onClick={() => resetSkipsMutation.mutate()}
              disabled={resetSkipsMutation.isPending}
            >
              {resetSkipsMutation.isPending
                ? "Đang mở lại..."
                : "Mở lại thẻ đã bỏ qua"}
            </button>
          </div>
          {/* `data === 0` means the click reopened nothing — every remaining
              card was matched, not skipped. Tell the user so the button
              doesn't feel inert. */}
          {resetSkipsMutation.isSuccess && resetSkipsMutation.data === 0 && (
            <p className="lead" style={{ marginTop: 12, color: "var(--muted)" }}>
              Không còn thẻ nào đã bỏ qua để mở lại.
            </p>
          )}
        </div>
      </section>
    );
  }

  const top = available[0];

  const handleSwipe = (id: string, direction: SwipeDirection) => {
    // Re-entrancy guard for fast double-taps on macOS trackpads / mobile.
    // TanStack Query's `isPending` flips after dispatch, but two synchronous
    // clicks can both pass through before the flag flips.
    if (matchMutation.isPending || skipMutation.isPending) return;
    if (direction === "right") {
      matchMutation.mutate(id);
      return;
    }
    skipMutation.mutate(id);
  };

  return (
    <section className="page deck-layout reference-discover">
      <div className="deck-stack">
        {/* `key` per card → SwipeCard remounts with fresh motion values, so the
            new top card starts centred instead of inheriting the last card's
            off-screen position. */}
        <SwipeCard
          key={top.id}
          character={top}
          busy={matchMutation.isPending || skipMutation.isPending}
          onSwipe={(direction) => handleSwipe(top.id, direction)}
        />
      </div>
      <aside className="deck-side">
        <div className="stat-grid">
          <div className="panel stat">
            <strong>{matches.length}</strong>
            <span>Đã chọn</span>
          </div>
          <div className="panel stat">
            <strong>{points}</strong>
            <span>Điểm</span>
          </div>
          <div className="panel stat">
            <strong>{completedChallenges}</strong>
            <span>Hoàn thành</span>
          </div>
        </div>
        <div className="panel source-panel">
          <p className="kicker">Gợi ý học tập</p>
          <h2 style={{ fontSize: 24 }}>Chọn để mở trò chuyện</h2>
          <p className="lead" style={{ fontSize: 15 }}>
            Mỗi nhân vật được chọn cộng 10 điểm và mở phòng trò chuyện. Làm
            thử thách đạt 4/5 để mở khóa hoàn toàn.
          </p>
          {top && (
            <p className="lead" style={{ fontSize: 13, color: "var(--muted)" }}>
              Đang xem: <strong>{top.name}</strong> · {top.work}
            </p>
          )}
        </div>
      </aside>
    </section>
  );
}
