import { useEffect, useState, type ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAppStore } from "@/stores/useAppStore";
import { realClient } from "@/api/realClient";
import { useReal } from "@/api/adapter";

type BootState = "checking" | "ready" | "missing";

export default function RequireProfile({ children }: { children: ReactNode }) {
  const profile = useAppStore((s) => s.profile);
  const setProfile = useAppStore((s) => s.setProfile);
  const setMatches = useAppStore((s) => s.setMatches);
  const location = useLocation();
  const [boot, setBoot] = useState<BootState>("checking");

  useEffect(() => {
    let cancelled = false;

    if (!useReal("auth")) {
      setBoot(profile ? "ready" : "missing");
      return;
    }

    realClient
      .getCurrentUser()
      .then((current) => {
        if (cancelled) return;
        setProfile(current.username, current.grade, current.userId, current.points);
        setBoot("ready");
      })
      .catch((err) => {
        if (cancelled) return;
        console.warn("OAuth session check failed, redirecting to login:", err);
        setBoot("missing");
      });

    return () => {
      cancelled = true;
    };
  }, [profile?.userId, setProfile]);

  // When the OAuth callback stores the profile, avoid a second loading frame.
  useEffect(() => {
    if (!useReal("auth") && profile) {
      setBoot("ready");
    }
  }, [profile]);

  // Reconcile local matches against the backend once auth is settled.
  //
  // Why: the FE persists a `matches: string[]` array in localStorage as a
  // cache of who the user has swiped right on. Two paths can cause it to
  // diverge from the backend record — (a) localStorage carried forward
  // from the mock-mode era when matches were never sent server-side; (b)
  // any other manual or migration-driven edit. Once stale entries exist
  // they're permanent until reset, and they cause `Chat`'s match guard to
  // let the user into a chat the backend then 403s on.
  //
  // Backend is the source of truth: `GET /users/{id}/matches` returns the
  // exact list of right-swiped characters. Replace local with that on
  // every profile-ready transition. In mock mode this sync is skipped
  // entirely (the local array IS the truth there).
  useEffect(() => {
    if (boot !== "ready") return;
    if (!profile?.userId) return;
    if (!useReal("match")) return;
    let cancelled = false;
    realClient.getMatchedSlugs().then(
      (slugs) => {
        if (!cancelled) setMatches(slugs);
      },
      (err) => {
        // Sync failure is non-fatal — local cache continues to be used
        // and individual chat 403s will heal themselves via removeMatch.
        console.warn("matches sync failed", err);
      },
    );
    return () => {
      cancelled = true;
    };
  }, [boot, profile?.userId, setMatches]);

  if (boot === "checking") {
    return (
      <section className="page narrow">
        <div className="card empty-state">
          <p className="lead">Đang chuẩn bị phiên...</p>
        </div>
      </section>
    );
  }

  if (boot === "missing" || (boot === "ready" && !profile)) {
    return <Navigate to="/onboarding" replace state={{ from: location }} />;
  }

  return <>{children}</>;
}
