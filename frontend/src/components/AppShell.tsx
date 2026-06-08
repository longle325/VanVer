import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useAppStore } from "@/stores/useAppStore";
import {
  Compass,
  BookOpen,
  Trophy,
  User,
  Flame,
  Medal,
  Volume2,
  VolumeX,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

interface NavItem {
  key: string;
  to: string;
  label: string;
  icon: LucideIcon;
}

const items: NavItem[] = [
  { key: "discover", to: "/discover", label: "Khám phá", icon: Compass },
  { key: "collection", to: "/collection", label: "Nhân vật đã chọn", icon: BookOpen },
  { key: "leaderboard", to: "/leaderboard", label: "Bảng xếp hạng", icon: Trophy },
  { key: "profile", to: "/profile", label: "Hồ sơ", icon: User },
];

export default function AppShell() {
  const profile = useAppStore((s) => s.profile);
  const points = useAppStore((s) => s.points);
  const streak = useAppStore((s) => s.streak);
  const musicEnabled = useAppStore((s) => s.music.enabled);
  const setMusicEnabled = useAppStore((s) => s.setMusicEnabled);
  const location = useLocation();
  const isLeaderboard = location.pathname.startsWith("/leaderboard");

  return (
    <div className="app-shell">
      <aside className="side-nav">
        <div className="brand">
          <h1 className="brand-title">LitMatch</h1>
          <p className="brand-subtitle">Văn học Việt Nam</p>
        </div>
        <nav className="nav-links">
          {items.map((item) => (
            <NavLink
              key={item.key}
              to={item.to}
              className={({ isActive }) =>
                `nav-link${isActive ? " active" : ""}`
              }
            >
              <item.icon size={22} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
      <header className="topbar">
        <div className="topbar-identity">
          <strong
            style={{
              color: "var(--cinnabar)",
              fontFamily: "'Noto Serif', serif",
              fontSize: 20,
            }}
          >
            LitMatch
          </strong>
          {profile && (
            <span style={{ marginLeft: 8, color: "var(--muted)", fontSize: 12 }}>
              Lớp {profile.grade}
            </span>
          )}
        </div>
        <div className="topbar-actions">
          <button
            type="button"
            role="switch"
            aria-checked={musicEnabled}
            aria-label={musicEnabled ? "Tắt nhạc nền" : "Bật nhạc nền"}
            title={musicEnabled ? "Tắt nhạc nền" : "Bật nhạc nền"}
            className={`global-sound-toggle${musicEnabled ? " is-on" : ""}`}
            onClick={() => setMusicEnabled(!musicEnabled)}
          >
            {musicEnabled ? (
              <Volume2 size={18} aria-hidden="true" />
            ) : (
              <VolumeX size={18} aria-hidden="true" />
            )}
            <span>{musicEnabled ? "Nhạc bật" : "Nhạc tắt"}</span>
          </button>
          <div className="topbar-metrics">
            <span className="metric">
              <Flame size={16} />
              {isLeaderboard ? "Thành tích: " : ""}
              {streak} Ngày
            </span>
            <span className="metric">
              <Medal size={16} />
              {isLeaderboard ? "Điểm: " : ""}
              {points.toLocaleString("vi-VN")} Điểm
            </span>
          </div>
        </div>
      </header>
      <main className="main">
        <Outlet />
      </main>
      {profile && (
        <nav className="mobile-nav">
          {items
            .filter((item) => item.key !== "profile")
            .map((item) => (
              <NavLink
                key={item.key}
                to={item.to}
                className={({ isActive }) =>
                  `nav-link${isActive ? " active" : ""}`
                }
              >
                <item.icon size={20} />
                <span>{item.label}</span>
              </NavLink>
            ))}
        </nav>
      )}
    </div>
  );
}
