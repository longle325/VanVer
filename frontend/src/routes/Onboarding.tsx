import { getOAuthLoginUrl } from "@/api/realClient";

export default function Onboarding() {
  const loginUrl = getOAuthLoginUrl("google", "/discover");

  return (
    <section className="onboarding-screen">
      <div className="onboarding-card">
        <p className="kicker">Đăng nhập</p>
        <h1 className="headline-lg">Chào mừng đến với Vanver</h1>
        <p className="lead">
          Dùng tài khoản Google để lưu tiến trình khám phá nhân vật, trò
          chuyện và thử thách văn học.
        </p>
        <div className="onboarding-actions">
          <a className="btn primary" href={loginUrl}>
            Đăng nhập bằng Google
          </a>
        </div>
      </div>
    </section>
  );
}
