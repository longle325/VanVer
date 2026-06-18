import { useEffect, useState, type ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAppStore } from "@/stores/useAppStore";
import { realClient } from "@/api/realClient";
import { useReal } from "@/api/adapter";
import type { SyncedProgress } from "@/types";

type BootState = "checking" | "ready" | "missing";

function mergeProgress(
  local: SyncedProgress,
  remote: SyncedProgress,
): SyncedProgress {
  const characterIds = new Set([
    ...Object.keys(local.levelResults),
    ...Object.keys(remote.levelResults),
  ]);
  const levelResults: SyncedProgress["levelResults"] = {};

  for (const characterId of characterIds) {
    levelResults[characterId] = {
      ...(local.levelResults[characterId] ?? {}),
      ...(remote.levelResults[characterId] ?? {}),
    };
  }

  return {
    completed: { ...local.completed, ...remote.completed },
    levelResults,
    skipped: Array.from(new Set([...local.skipped, ...remote.skipped])),
  };
}

function currentProgressSnapshot(): SyncedProgress {
  const state = useAppStore.getState();
  return {
    completed: state.completed,
    levelResults: state.levelResults,
    skipped: state.skipped,
  };
}

export default function RequireProfile({ children }: { children: ReactNode }) {
  const profile = useAppStore((s) => s.profile);
  const completed = useAppStore((s) => s.completed);
  const levelResults = useAppStore((s) => s.levelResults);
  const skipped = useAppStore((s) => s.skipped);
  const setProfile = useAppStore((s) => s.setProfile);
  const setMatches = useAppStore((s) => s.setMatches);
  const setProgress = useAppStore((s) => s.setProgress);
  const location = useLocation();
  const [boot, setBoot] = useState<BootState>("checking");
  const [progressHydrated, setProgressHydrated] = useState(false);

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

  useEffect(() => {
    if (boot !== "ready") return;
    if (!profile?.userId) return;
    if (!useReal("auth")) {
      setProgressHydrated(true);
      return;
    }

    let cancelled = false;
    setProgressHydrated(false);
    realClient.getProgress().then(
      (remote) => {
        if (cancelled) return;
        const merged = mergeProgress(currentProgressSnapshot(), remote);
        setProgress(merged);
        setProgressHydrated(true);
      },
      (err) => {
        if (cancelled) return;
        console.warn("progress sync failed", err);
        setProgressHydrated(true);
      },
    );
    return () => {
      cancelled = true;
    };
  }, [boot, profile?.userId, setProgress]);

  useEffect(() => {
    if (boot !== "ready") return;
    if (!profile?.userId) return;
    if (!progressHydrated) return;
    if (!useReal("auth")) return;

    const progress = { completed, levelResults, skipped };
    const timeout = window.setTimeout(() => {
      realClient.saveProgress(progress).catch((err) => {
        console.warn("progress save failed", err);
      });
    }, 500);
    return () => window.clearTimeout(timeout);
  }, [
    boot,
    profile?.userId,
    progressHydrated,
    completed,
    levelResults,
    skipped,
  ]);

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
