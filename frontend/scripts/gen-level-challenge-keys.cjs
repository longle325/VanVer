/**
 * Generate the backend's level-challenge grading keys from the canonical
 * frontend definitions so the two can never drift.
 *
 * Source of truth: frontend/src/data/levelChallenges.ts (rendered by the UI).
 * Output: backend/data/level_challenges.json (read by the grading endpoint).
 *
 * Run from the frontend/ directory:  node scripts/gen-level-challenge-keys.cjs
 */
const fs = require("fs");
const path = require("path");
const esbuild = require("esbuild");

const SRC = path.resolve(__dirname, "../src/data/levelChallenges.ts");
const OUT = path.resolve(__dirname, "../../backend/data/level_challenges.json");

const tsSource = fs.readFileSync(SRC, "utf8");
// The only import is a type-only `import type { ... } from "@/types"`, which
// esbuild erases. No runtime imports remain, so the CJS output is evaluable.
const { code } = esbuild.transformSync(tsSource, { loader: "ts", format: "cjs" });
const moduleShim = { exports: {} };
new Function("module", "exports", "require", code)(moduleShim, moduleShim.exports, require);

const map = moduleShim.exports.levelChallengeMap;
if (!map || typeof map !== "object") {
  throw new Error("levelChallengeMap not found in source module");
}

const out = {};
for (const [slug, levels] of Object.entries(map)) {
  out[slug] = levels.map((lv) => ({
    level: lv.level,
    phaseTitle: lv.phaseTitle,
    questions: lv.questions.map((q) => ({
      id: q.id,
      type: q.type,
      // MCQ answer index; -1 for open-ended.
      answer: typeof q.answer === "number" ? q.answer : -1,
      text: q.text,
      rubric: q.rubric ?? null,
      evidence: q.evidence ?? null,
    })),
  }));
}

fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, JSON.stringify(out, null, 2) + "\n");

const slugs = Object.keys(out);
const levelCount = slugs.reduce((n, s) => n + out[s].length, 0);
console.log(`Wrote ${OUT}`);
console.log(`  ${slugs.length} characters, ${levelCount} levels`);
