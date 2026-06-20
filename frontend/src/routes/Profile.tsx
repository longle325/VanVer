import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/api/client";
import { useAppStore } from "@/stores/useAppStore";
import MusicSettingsCard from "@/components/MusicSettingsCard";
import { countAttemptedChallenges } from "@/lib/progressStats";

export default function Profile() {
  const navigate = useNavigate();
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const profile = useAppStore((s) => s.profile);
  const points = useAppStore((s) => s.points);
  const matches = useAppStore((s) => s.matches);
  const completed = useAppStore((s) => s.completed);
  const levelResults = useAppStore((s) => s.levelResults);
  const resetAll = useAppStore((s) => s.resetAll);
  const attemptedChallenges = countAttemptedChallenges(completed, levelResults);

  const handleLogout = async () => {
    if (isLoggingOut) return;
    setIsLoggingOut(true);
    try {
      await api.logout();
    } catch (err) {
      console.warn("Logout request failed; clearing local session anyway.", err);
    } finally {
      resetAll();
      navigate("/onboarding", { replace: true });
    }
  };

  return (
    <section className="page narrow">
      <div className="profile-card card">
        <p className="kicker">Hồ sơ</p>
        <h1 className="headline-lg">{profile?.username}</h1>
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
        <div className="actions-row">
          <button
            type="button"
            className="btn secondary"
            onClick={handleLogout}
            disabled={isLoggingOut}
          >
            {isLoggingOut ? "Đang đăng xuất..." : "Đăng xuất"}
          </button>
          <button
            type="button"
            className="btn ghost"
            onClick={() => {
              resetAll();
              navigate("/onboarding", { replace: true });
            }}
            disabled={isLoggingOut}
          >
            Đặt lại dữ liệu thử nghiệm
          </button>
        </div>
      </div>
      <MusicSettingsCard />
    </section>
  );
}
