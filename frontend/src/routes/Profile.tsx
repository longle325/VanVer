import { useAppStore } from "@/stores/useAppStore";
import MusicSettingsCard from "@/components/MusicSettingsCard";
import { countAttemptedChallenges } from "@/lib/progressStats";

export default function Profile() {
  const profile = useAppStore((s) => s.profile);
  const points = useAppStore((s) => s.points);
  const matches = useAppStore((s) => s.matches);
  const completed = useAppStore((s) => s.completed);
  const levelResults = useAppStore((s) => s.levelResults);
  const attemptedChallenges = countAttemptedChallenges(completed, levelResults);

  return (
    <section className="page narrow">
      <div className="profile-card card">
        <p className="kicker">Hồ sơ</p>
        <h1 className="headline-lg">{profile?.username}</h1>
        <p className="lead">Lớp {profile?.grade}</p>
        <div className="profile-meta">
          <div className="panel stat">
            <strong>{points}</strong>
            <span>Điểm</span>
          </div>
          <div className="panel stat">
            <strong>{matches.length}</strong>
            <span>Nhân vật đã chọn</span>
          </div>
          <div className="panel stat">
            <strong>{attemptedChallenges}</strong>
            <span>Thử thách đã làm</span>
          </div>
        </div>
      </div>
      <MusicSettingsCard />
    </section>
  );
}
