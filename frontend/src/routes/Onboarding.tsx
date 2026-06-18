import { Volume2, VolumeX } from "lucide-react";
import { getOAuthLoginUrl } from "@/api/realClient";
import { useAppStore } from "@/stores/useAppStore";

const galleryCards = [
  {
    name: "Chí Phèo",
    work: "Chí Phèo",
    image: "/characters/chi-pheo.webp",
  },
  {
    name: "Thúy Kiều",
    work: "Truyện Kiều",
    image: "/characters/thuy-kieu-1.webp",
  },
  {
    name: "Mị",
    work: "Vợ chồng A Phủ",
    image: "/characters/mi-1.webp",
  },
  {
    name: "Vũ Nương",
    work: "Chuyện người con gái Nam Xương",
    image: "/characters/vu-nuong.webp",
  },
];

function GoogleGIcon() {
  return (
    <svg
      className="google-g-icon"
      viewBox="0 0 24 24"
      width="20"
      height="20"
      aria-hidden="true"
      focusable="false"
    >
      <path
        fill="#4285F4"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      />
      <path
        fill="#34A853"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
      />
      <path
        fill="#FBBC05"
        d="M5.84 14.1c-.22-.66-.35-1.36-.35-2.1s.13-1.44.35-2.1V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l3.66-2.84z"
      />
      <path
        fill="#EA4335"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06L5.84 9.9C6.71 7.3 9.14 5.38 12 5.38z"
      />
    </svg>
  );
}

export default function Onboarding() {
  const loginUrl = getOAuthLoginUrl("google", "/discover");
  const musicEnabled = useAppStore((s) => s.music.enabled);
  const setMusicEnabled = useAppStore((s) => s.setMusicEnabled);

  return (
    <section className="onboarding-screen">
      <button
        type="button"
        className={`onboarding-music-toggle${musicEnabled ? " is-on" : ""}`}
        aria-label={musicEnabled ? "Tắt nhạc nền" : "Bật nhạc nền"}
        aria-pressed={musicEnabled}
        onClick={() => setMusicEnabled(!musicEnabled)}
      >
        {musicEnabled ? <Volume2 size={20} /> : <VolumeX size={20} />}
      </button>

      <div className="onboarding-gallery" aria-hidden="true">
        {galleryCards.map((card, index) => (
          <article
            key={card.name}
            className={`onboarding-gallery-card card-${index + 1}`}
          >
            <img src={card.image} alt="" />
            <div className="onboarding-gallery-caption">
              <strong>{card.name}</strong>
              <span>{card.work}</span>
            </div>
          </article>
        ))}
      </div>

      <div className="onboarding-stage">
        <div className="onboarding-card">
          <h1 className="headline-lg onboarding-brand">Vanver</h1>
          <p className="onboarding-tagline">Hẹn hò với nhân vật văn học</p>

          <div className="onboarding-actions">
            <a className="btn google-login-button" href={loginUrl}>
              <GoogleGIcon />
              <span>Đăng nhập bằng Google</span>
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
