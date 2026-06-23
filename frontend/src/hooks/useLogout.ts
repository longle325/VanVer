import { useCallback, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { api } from "@/api/client";
import { useAppStore } from "@/stores/useAppStore";

export function useLogout() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const resetAll = useAppStore((s) => s.resetAll);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const pendingRef = useRef(false);

  const logout = useCallback(async () => {
    if (pendingRef.current) return;

    pendingRef.current = true;
    setIsLoggingOut(true);
    try {
      await api.logout();
    } catch (err) {
      console.warn("Logout request failed; clearing local session anyway.", err);
    } finally {
      queryClient.clear();
      resetAll();
      navigate("/onboarding", { replace: true });
      pendingRef.current = false;
      setIsLoggingOut(false);
    }
  }, [navigate, queryClient, resetAll]);

  return { isLoggingOut, logout };
}
