import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import AppShell from "@/components/AppShell";
import AuthBackgroundMusic from "@/components/AuthBackgroundMusic";
import BackgroundMusic from "@/components/BackgroundMusic";
import RequireProfile from "@/components/RequireProfile";
import { usePrefetchCatalog } from "@/api/queries";
import Onboarding from "@/routes/Onboarding";
import Discover from "@/routes/Discover";
import Collection from "@/routes/Collection";
import Chat from "@/routes/Chat";
import Challenge from "@/routes/Challenge";
import Leaderboard from "@/routes/Leaderboard";
import Profile from "@/routes/Profile";
import CharacterProfile from "@/routes/CharacterProfile";

export default function App() {
  const { pathname } = useLocation();
  const isAuthRoute = pathname === "/onboarding" || pathname.startsWith("/auth/");
  usePrefetchCatalog();

  return (
    <>
      <BackgroundMusic />
      {isAuthRoute && <AuthBackgroundMusic />}
      <Routes>
        <Route path="/onboarding" element={<Onboarding />} />
        <Route
          element={
            <RequireProfile>
              <AppShell />
            </RequireProfile>
          }
        >
          <Route path="/discover" element={<Discover />} />
          <Route path="/collection" element={<Collection />} />
          <Route path="/characters/:id" element={<CharacterProfile />} />
          <Route path="/characters/:id/chat" element={<Chat />} />
          <Route path="/characters/:id/challenge" element={<Challenge />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/profile" element={<Profile />} />
        </Route>
        <Route path="*" element={<Navigate to="/discover" replace />} />
      </Routes>
    </>
  );
}
