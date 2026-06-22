import { useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { useAppStore } from "@/stores/useAppStore";

export const queryKeys = {
  deck: ["deck"] as const,
  characters: ["characters"] as const,
  character: (id: string) => ["character", id] as const,
  challenge: (id: string) => ["challenge", id] as const,
  leaderboard: ["leaderboard"] as const,
};

// The character catalog is effectively static content but the backend has a
// slow TTFB, so cache it aggressively and keep it across navigation to avoid
// refetching it (and blocking the Collection mount) every time.
const CATALOG_STALE_MS = 30 * 60_000;
const CATALOG_GC_MS = 60 * 60_000;

export function useDeck() {
  // The deck is user- and swipe-state-specific (keyed only ["deck"]), so it
  // intentionally keeps the default freshness rather than the static-catalog
  // policy below — avoids serving a stale deck across account switches.
  return useQuery({
    queryKey: queryKeys.deck,
    queryFn: api.getDeck,
  });
}

export function useAllCharacters() {
  return useQuery({
    queryKey: queryKeys.characters,
    queryFn: api.getAllCharacters,
    staleTime: CATALOG_STALE_MS,
    gcTime: CATALOG_GC_MS,
  });
}

export function useCharacter(id: string | undefined) {
  return useQuery({
    queryKey: queryKeys.character(id ?? ""),
    queryFn: () => api.getCharacter(id as string),
    enabled: !!id,
    staleTime: CATALOG_STALE_MS,
    gcTime: CATALOG_GC_MS,
  });
}

/**
 * Warm the character catalog as soon as the app mounts so the first visit to
 * Collection/Discover doesn't pay the backend's 2-4s TTFB on the render path.
 */
export function usePrefetchCatalog() {
  const queryClient = useQueryClient();
  useEffect(() => {
    queryClient.prefetchQuery({
      queryKey: queryKeys.characters,
      queryFn: api.getAllCharacters,
      staleTime: CATALOG_STALE_MS,
    });
  }, [queryClient]);
}

export function useChallenge(id: string | undefined) {
  return useQuery({
    queryKey: queryKeys.challenge(id ?? ""),
    queryFn: () => api.getChallenge(id as string),
    enabled: !!id,
  });
}

export function useLeaderboard() {
  return useQuery({
    queryKey: queryKeys.leaderboard,
    queryFn: api.getLeaderboard,
  });
}

export function useMatchMutation() {
  const matchCharacter = useAppStore((state) => state.matchCharacter);
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.recordMatch(id);
      matchCharacter(id);
      return id;
    },
    onSuccess: () => {
      // Backend dropped this character from the deck and added points to
      // the user; refresh both views so a navigation hits fresh data.
      queryClient.invalidateQueries({ queryKey: queryKeys.deck });
      queryClient.invalidateQueries({ queryKey: queryKeys.leaderboard });
    },
  });
}

export function useSkipMutation() {
  const skipCharacter = useAppStore((state) => state.skipCharacter);
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      // Server-first so a backend failure leaves local state in sync with
      // the server (the deck won't lie about a swipe that didn't persist).
      await api.recordSkip(id);
      skipCharacter(id);
      return id;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.deck });
    },
  });
}

export function useResetSkipsMutation() {
  const resetSkipped = useAppStore((state) => state.resetSkipped);
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      // Server-first: the deck is computed from the backend's swipe records,
      // so the skips must be cleared there before the local mirror, otherwise
      // a deck refetch would re-hide the cards we just reopened.
      await api.resetSkips();
      resetSkipped();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.deck });
    },
  });
}

export function useSubmitChallengeMutation() {
  const saveChallenge = useAppStore((state) => state.saveChallenge);
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, answers }: { id: string; answers: number[] }) => {
      const result = await api.submitChallenge(id, answers);
      saveChallenge(id, result);
      return result;
    },
    onSuccess: () => {
      // Points and characters_unlocked changed on the backend; refresh
      // the leaderboard so /leaderboard reflects the new score.
      queryClient.invalidateQueries({ queryKey: queryKeys.leaderboard });
    },
  });
}
