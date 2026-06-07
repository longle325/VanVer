import { useState } from "react";
import { Link } from "react-router-dom";
import { ShieldCheck, LockOpen, ChevronDown } from "lucide-react";
import { useAllCharacters } from "@/api/queries";
import { useAppStore } from "@/stores/useAppStore";
import CharacterArt from "@/components/CharacterArt";
import LevelProgress from "@/components/LevelProgress";
import {
  getLevelImages,
  getLevelProgressPercent,
  getUnlockedCharacterLevel,
  type LevelResults,
} from "@/lib/characterLevels";
import type { Character, ChallengeResult } from "@/types";

type SortKey = "level" | "recent" | "progress";

const SORT_LABEL: Record<SortKey, string> = {
  level: "Cấp độ nhân vật",
  recent: "Mới thêm gần đây",
  progress: "Tiến độ thử thách",
};

function CollectionCard({
  character,
  result,
  levelResults,
}: {
  character: Character;
  result?: ChallengeResult;
  levelResults: LevelResults;
}) {
  const currentLevel = getUnlockedCharacterLevel(character, levelResults);
  const progress = getLevelProgressPercent(character, levelResults, result);
  const hasLevels = Boolean(character.levelChallenges?.length);
  const isFullyComplete = character.levelChallenges?.length
    ? currentLevel === 3 && result?.passed
    : result?.passed;
  const status = isFullyComplete
    ? "Đã mở khóa hoàn toàn"
    : "Chưa hoàn thành thử thách";
  const image =
    character.portrait || getLevelImages(character, levelResults)[0] || character.image;

  return (
    <article className="card collection-card">
      <Link
        to={`/characters/${character.id}`}
        className="collection-image collection-image-link"
        aria-label={`Xem hồ sơ ${character.name}`}
      >
        {image ? (
          <img src={image} alt={character.name} />
        ) : (
          <CharacterArt character={character} />
        )}
        <span className={`collection-status level-${currentLevel}`}>
          {isFullyComplete ? <ShieldCheck size={14} /> : <LockOpen size={14} />}
          Level {currentLevel}
        </span>
      </Link>
      <div className="collection-body">
        <h2>
          <Link to={`/characters/${character.id}`} className="collection-name-link">
            {character.name}
          </Link>
        </h2>
        <p>{character.work}</p>
        {hasLevels ? (
          <LevelProgress
            character={character}
            levelResults={levelResults}
            compact
            className="collection-level-progress"
          />
        ) : (
          <div className="collection-progress">
            <span style={{ width: `${progress}%` }} />
          </div>
        )}
        <small>{progress}% khám phá</small>
        <span className={`badge ${isFullyComplete ? "done" : "pending"}`}>
          {status}
        </span>
        <div className="actions-row">
          <Link
            className="btn secondary"
            to={`/characters/${character.id}/chat`}
          >
            Trò chuyện
          </Link>
          <Link
            className="btn ghost"
            to={`/characters/${character.id}/challenge`}
          >
            Làm thử thách
          </Link>
          <Link
            className="btn ghost"
            to={`/characters/${character.id}`}
          >
            Hồ sơ
          </Link>
        </div>
      </div>
    </article>
  );
}

export default function Collection() {
  // Collection needs the FULL character catalog, not the deck.
  // `useDeck()` in real mode only returns UNSWIPED characters (backend
  // filter), so any matched character would be filtered out and the
  // collection would render empty — which is the bug we're fixing.
  const { data: catalog = [] } = useAllCharacters();
  const matches = useAppStore((s) => s.matches);
  const completed = useAppStore((s) => s.completed);
  const levelResults = useAppStore((s) => s.levelResults);
  const [sort, setSort] = useState<SortKey>("level");
  const [open, setOpen] = useState(false);

  const matched = catalog
    .filter((character) => matches.includes(character.id))
    .map((character) => ({
      character,
      matchedAt: matches.indexOf(character.id),
      level: getUnlockedCharacterLevel(character, levelResults),
      progress: getLevelProgressPercent(
        character,
        levelResults,
        completed[character.id],
      ),
    }))
    .sort((a, b) => {
      if (sort === "level") {
        return (
          b.level - a.level ||
          b.progress - a.progress ||
          b.matchedAt - a.matchedAt
        );
      }
      if (sort === "progress") return b.progress - a.progress;
      return b.matchedAt - a.matchedAt;
    });

  return (
    <section className="page reference-collection">
      <div className="collection-head">
        <div>
          <h1 className="headline-lg">Vòng tròn văn chương</h1>
          <p className="lead">
            Những nhân vật bạn đã khám phá trong hành trình học tập.
          </p>
        </div>
        <div className="sort-control">
          <span>Sắp xếp:</span>
          <div className="sort-menu">
            <button
              type="button"
              className="btn ghost"
              aria-haspopup="listbox"
              aria-expanded={open}
              onClick={() => setOpen((v) => !v)}
            >
              {SORT_LABEL[sort]}{" "}
              <ChevronDown size={16} />
            </button>
            {open && (
              <ul role="listbox" className="sort-options">
                {(Object.keys(SORT_LABEL) as SortKey[]).map((key) => (
                  <li key={key}>
                    <button
                      type="button"
                      role="option"
                      aria-selected={sort === key}
                      className={sort === key ? "active" : ""}
                      onClick={() => {
                        setSort(key);
                        setOpen(false);
                      }}
                    >
                      {SORT_LABEL[key]}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
      {matched.length ? (
        <div className="grid collection-grid">
          {matched.map(({ character }) => (
            <CollectionCard
              key={character.id}
              character={character}
              result={completed[character.id]}
              levelResults={levelResults}
            />
          ))}
        </div>
      ) : (
        <div className="card empty-state">
          <h2>Chưa có nhân vật nào</h2>
          <p className="lead">
            Hãy vào Khám phá và chọn một nhân vật để mở trò chuyện.
          </p>
          <Link className="btn primary" to="/discover">
            Đi khám phá
          </Link>
        </div>
      )}
    </section>
  );
}
