/**
 * API router. Each method picks `realClient` or `mockClient` based on the
 * `VITE_REAL_ENDPOINTS` env flag, so endpoints can flip from mock to real
 * one at a time.
 *
 * Callers (route files, hooks in queries.ts) import `api` and never reach
 * past this seam. The two underlying clients implement the same `ApiClient`
 * interface defined in `./types.ts`.
 */

import { mockClient } from "./mockClient";
import { realClient } from "./realClient";
import { useReal } from "./adapter";
import type { ApiClient, ChatRequest } from "./types";

export type { ApiClient, ChatRequest, CreateUserInput } from "./types";
export { ApiError } from "./adapter";

export const api: ApiClient = {
  createUser: (input) =>
    useReal("auth")
      ? realClient.createUser(input)
      : mockClient.createUser(input),

  getCurrentUser: () =>
    useReal("auth")
      ? realClient.getCurrentUser()
      : mockClient.getCurrentUser(),

  getDeck: () =>
    useReal("deck") ? realClient.getDeck() : mockClient.getDeck(),

  getAllCharacters: () =>
    useReal("characters")
      ? realClient.getAllCharacters()
      : mockClient.getAllCharacters(),

  getCharacter: (id) =>
    useReal("characters")
      ? realClient.getCharacter(id)
      : mockClient.getCharacter(id),

  recordMatch: (id) =>
    useReal("match")
      ? realClient.recordMatch(id)
      : mockClient.recordMatch(id),

  recordSkip: (id) =>
    useReal("match") ? realClient.recordSkip(id) : mockClient.recordSkip(id),

  getMatchedSlugs: () =>
    useReal("match")
      ? realClient.getMatchedSlugs()
      : mockClient.getMatchedSlugs(),

  getProgress: () =>
    useReal("auth") ? realClient.getProgress() : mockClient.getProgress(),

  saveProgress: (progress) =>
    useReal("auth")
      ? realClient.saveProgress(progress)
      : mockClient.saveProgress(progress),

  getChallenge: (id) =>
    useReal("challenge")
      ? realClient.getChallenge(id)
      : mockClient.getChallenge(id),

  submitChallenge: (id, answers) =>
    useReal("challenge")
      ? realClient.submitChallenge(id, answers)
      : mockClient.submitChallenge(id, answers),

  gradeOpenEndedAnswer: (input) =>
    useReal("challenge")
      ? realClient.gradeOpenEndedAnswer(input)
      : mockClient.gradeOpenEndedAnswer(input),

  getLeaderboard: () =>
    useReal("leaderboard")
      ? realClient.getLeaderboard()
      : mockClient.getLeaderboard(),

  getChatHistory: (id) =>
    useReal("chat")
      ? realClient.getChatHistory(id)
      : mockClient.getChatHistory(id),

  streamChat: (input: ChatRequest) =>
    useReal("chat")
      ? realClient.streamChat(input)
      : mockClient.streamChat(input),
};

// Underlying clients are exported for tests / advanced wiring. Production
// code should always go through `api`.
export { mockClient, realClient };
