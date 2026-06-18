import { useLeaderboard } from "@/api/queries";
import { useAppStore } from "@/stores/useAppStore";
import type { LeaderboardEntry } from "@/types";

export default function Leaderboard() {
  const { data: demo = [] } = useLeaderboard();
  const profile = useAppStore((s) => s.profile);
  const points = useAppStore((s) => s.points);
  const completed = useAppStore((s) => s.completed);

  const currentName = profile?.username || "Bạn";
  const currentUnlocked = Object.values(completed).filter((r) => r.passed).length;

  // If the backend response already includes the current user (matched by
  // userId — present in real mode), use those entries verbatim so we don't
  // double-list. Otherwise fall back to the legacy mock-merge behavior where
  // we synthesize a "Bạn" row from local Zustand state.
  const includesCurrentUser =
    profile?.userId !== undefined &&
    demo.some((entry) => entry.userId === profile.userId);

  const rows = (
    includesCurrentUser
      ? demo
      : [...demo, { name: currentName, points, unlocked: currentUnlocked }]
  ).sort((a, b) => b.points - a.points);

  const isCurrentRow = (row: LeaderboardEntry) =>
    profile?.userId !== undefined
      ? row.userId === profile.userId
      : row.name === currentName;

  return (
    <section className="page reference-leaderboard">
      <h1 className="headline-lg">Hào kiệt văn chương</h1>
      <p className="lead">
        Nơi vinh danh những học giả uyên bác trên hành trình khám phá văn học
        Việt Nam.
      </p>
      <div className="leader-tabs">
        <button className="active">Global</button>
      </div>
      <div className="card leaderboard">
        <div className="leader-row header">
          <span>Hạng</span>
          <span>Tên học giả</span>
          <span>Nhân vật đã mở khóa</span>
          <span>Tổng điểm</span>
        </div>
        {rows.map((row, index) => {
          const isCurrent = isCurrentRow(row);
          const initials = row.name
            .split(" ")
            .map((part) => part[0])
            .join("")
            .slice(0, 2);
          return (
            <div
              key={`${row.name}-${index}`}
              className={`leader-row${isCurrent ? " current" : ""}`}
            >
              <span className="rank">{index + 1}</span>
              <span className="leader-name">
                <span className="leader-avatar">{initials}</span>
                <strong>{isCurrent ? "Bạn" : row.name}</strong>
              </span>
              <span>{row.unlocked}</span>
              <strong>{row.points.toLocaleString("vi-VN")}</strong>
            </div>
          );
        })}
      </div>
    </section>
  );
}
