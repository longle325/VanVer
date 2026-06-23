import { useEffect, useMemo, useState, type FormEvent } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { LogOut, Save } from "lucide-react";
import { api } from "@/api/client";
import { queryKeys } from "@/api/queries";
import { useAppStore } from "@/stores/useAppStore";
import MusicSettingsCard from "@/components/MusicSettingsCard";
import { useLogout } from "@/hooks/useLogout";
import { countAttemptedChallenges } from "@/lib/progressStats";

export default function Profile() {
  const queryClient = useQueryClient();
  const profile = useAppStore((s) => s.profile);
  const points = useAppStore((s) => s.points);
  const matches = useAppStore((s) => s.matches);
  const completed = useAppStore((s) => s.completed);
  const levelResults = useAppStore((s) => s.levelResults);
  const setProfile = useAppStore((s) => s.setProfile);
  const { isLoggingOut, logout } = useLogout();
  const [displayName, setDisplayName] = useState(profile?.username ?? "");
  const [isSavingName, setIsSavingName] = useState(false);
  const [nameStatus, setNameStatus] = useState<
    { kind: "success" | "error"; message: string } | null
  >(null);
  const attemptedChallenges = countAttemptedChallenges(completed, levelResults);
  const normalizedDisplayName = displayName.trim();
  const currentDisplayName = useMemo(
    () => (profile?.username ?? "").trim(),
    [profile?.username],
  );
  const canSaveName =
    normalizedDisplayName.length > 0 &&
    normalizedDisplayName !== currentDisplayName &&
    !isSavingName &&
    !isLoggingOut;

  useEffect(() => {
    setDisplayName(profile?.username ?? "");
  }, [profile?.username]);

  const handleDisplayNameSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!profile || !canSaveName) return;

    setIsSavingName(true);
    setNameStatus(null);
    try {
      const updated = await api.updateDisplayName({
        displayName: normalizedDisplayName,
      });
      setProfile(updated.username, updated.grade, updated.userId, updated.points);
      queryClient.invalidateQueries({ queryKey: queryKeys.leaderboard });
      setNameStatus({ kind: "success", message: "Đã lưu tên hiển thị." });
    } catch (err) {
      console.warn("Display name update failed", err);
      setNameStatus({
        kind: "error",
        message: "Chưa lưu được tên hiển thị.",
      });
    } finally {
      setIsSavingName(false);
    }
  };

  return (
    <section className="page narrow">
      <div className="profile-card card">
        <p className="kicker">Hồ sơ</p>
        <h1 className="headline-lg">{profile?.username}</h1>
        <form className="profile-name-form" onSubmit={handleDisplayNameSubmit}>
          <label className="profile-field">
            <span>Tên hiển thị</span>
            <input
              value={displayName}
              maxLength={120}
              onChange={(event) => {
                setDisplayName(event.target.value);
                setNameStatus(null);
              }}
              disabled={isSavingName || isLoggingOut}
            />
          </label>
          <div className="profile-save-row">
            <button
              type="submit"
              className="btn secondary"
              disabled={!canSaveName}
            >
              <Save size={18} aria-hidden="true" />
              {isSavingName ? "Đang lưu..." : "Lưu tên"}
            </button>
            {nameStatus && (
              <p className={`profile-status ${nameStatus.kind}`}>
                {nameStatus.message}
              </p>
            )}
          </div>
        </form>
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
            onClick={logout}
            disabled={isLoggingOut}
          >
            <LogOut size={18} aria-hidden="true" />
            {isLoggingOut ? "Đang đăng xuất..." : "Đăng xuất"}
          </button>
        </div>
      </div>
      <MusicSettingsCard />
    </section>
  );
}
