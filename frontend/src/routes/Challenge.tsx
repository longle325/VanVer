import { type CSSProperties, useEffect, useMemo, useState } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { CheckCircle, Sparkles } from "lucide-react";
import { api } from "@/api/client";
import {
  queryKeys,
  useCharacter,
  useSubmitChallengeMutation,
} from "@/api/queries";
import { useAppStore } from "@/stores/useAppStore";
import {
  getActiveChallengeLevel,
  getLevelImages,
  getLevelResult,
  type LevelResults,
} from "@/lib/characterLevels";
import { scoreLevelChallenge } from "@/lib/scoring";
import LevelProgress from "@/components/LevelProgress";
import LevelUpOverlay from "@/components/LevelUpOverlay";
import type {
  Character,
  CharacterLevelChallenge,
  ChallengeQuestion,
  ChallengeResult,
  OpenEndedGradeResult,
  SyncedProgress,
} from "@/types";

type AnswerValue = number | string;

function isOpenQuestion(question: ChallengeQuestion): boolean {
  return question.type === "open_ended";
}

function currentProgressSnapshot(): SyncedProgress {
  const state = useAppStore.getState();
  return {
    completed: state.completed,
    levelResults: state.levelResults,
    skipped: state.skipped,
  };
}

function ResultView({
  character,
  questions,
  result,
  levelChallenge,
  levelResults,
  onRetry,
  onContinue,
}: {
  character: Character;
  questions: ChallengeQuestion[];
  result: ChallengeResult;
  levelChallenge?: CharacterLevelChallenge;
  levelResults: LevelResults;
  onRetry: () => void;
  onContinue?: () => void;
}) {
  const total = result.total ?? questions.length;
  const isLevelMode = Boolean(levelChallenge);
  const unlockedLevel = result.nextLevelUnlocked;
  const levelImages = getLevelImages(character, levelResults);
  const resultBackgroundStyle = levelImages[0]
    ? ({
        "--challenge-bg-image": `url(${levelImages[0]})`,
      } as CSSProperties)
    : undefined;
  const reviewItems = useMemo(
    () =>
      questions.map((question, index) => {
        const picked = result.answers[index];
        // In real mode `question.answer` is a -1 stub (server hides it
        // pre-submission); the authoritative correct index comes back in
        // `result.correctAnswers`. Fall back to the seed value for mock.
        const correctIndex = result.correctAnswers?.[index] ?? question.answer;
        const isOpen = isOpenQuestion(question);
        const openGrade = result.openGrades?.[question.id];
        const isCorrect = isOpen
          ? Boolean(openGrade?.passed)
          : picked === correctIndex;
        const pickedIndex = typeof picked === "number" ? picked : undefined;
        const answerText =
          typeof picked === "string" && picked.trim() ? picked : "Chưa trả lời";
        const gradeText = openGrade
          ? openGrade.passed
            ? "Đạt"
            : "Chưa đạt"
          : "Chưa có kết quả chấm";
        const gradeReason =
          openGrade?.feedback ||
          (openGrade
            ? "Chưa có nhận xét chi tiết."
            : "Câu này chưa có dữ liệu chấm để hiển thị.");

        return {
          answerText,
          correctIndex,
          gradeReason,
          gradeText,
          index,
          isCorrect,
          isOpen,
          openGrade,
          pickedIndex,
          question,
        };
      }),
    [questions, result.answers, result.correctAnswers, result.openGrades],
  );
  const firstReviewIndex = Math.max(
    0,
    reviewItems.findIndex((item) => !item.isCorrect),
  );
  const [selectedReviewIndex, setSelectedReviewIndex] =
    useState(firstReviewIndex);
  const selectedReview = reviewItems[selectedReviewIndex] ?? reviewItems[0];

  useEffect(() => {
    setSelectedReviewIndex(firstReviewIndex);
  }, [firstReviewIndex]);

  return (
    <section
      className="reference-challenge challenge-stage challenge-result-stage"
      style={resultBackgroundStyle}
    >
      <div className="challenge-stage-art" aria-hidden="true" />
      <div className="challenge-stage-inner result-stage-inner">
        <header className="challenge-hero result-hero">
          <p className="challenge-eyebrow">
            {isLevelMode
              ? `Kết quả Level ${result.level}`
              : "Kết quả thử thách"}
          </p>
          <h1 className="headline-lg">
            {character.name}: {result.score}/{total} câu đạt
          </h1>
          {levelChallenge && (
            <p className="result-phase-copy">{levelChallenge.phaseTitle}</p>
          )}
          {isLevelMode && (
            <LevelProgress
              character={character}
              levelResults={levelResults}
              className="challenge-level-progress result-level-progress"
            />
          )}
        </header>

        {unlockedLevel && (
          <div className="level-up-banner result-unlock-banner" role="status">
            <Sparkles size={22} />
            <span>
              Mở khóa Level {unlockedLevel}:{" "}
              {character.levels?.find((level) => level.level === unlockedLevel)
                ?.title ?? "giai đoạn mới"}
            </span>
          </div>
        )}

        <p className="lead result-message">
          {result.passed
            ? unlockedLevel
              ? "Bạn đã hoàn thành giai đoạn này. Ảnh nhân vật trong bộ sưu tập sẽ chuyển sang level mới."
              : "Bạn đã hoàn thành giai đoạn hiện tại. Bạn hiểu được các lớp động cơ và bối cảnh chính của nhân vật."
            : "Chưa đạt mốc 4/5. Hãy đọc giải thích rồi làm lại để củng cố kiến thức."}
        </p>

        <div className="stat-grid result-stat-grid">
          <div className="panel stat result-stat">
            <strong>+{result.awarded}</strong>
            <span>Điểm nhận được</span>
          </div>
          <div className="panel stat result-stat">
            <strong>{result.passed ? "Đạt" : "Chưa đạt"}</strong>
            <span>Trạng thái</span>
          </div>
          <div className="panel stat result-stat">
            <strong>{result.perfect ? `${total}/${total}` : "4/5"}</strong>
            <span>Mốc mở khóa</span>
          </div>
        </div>

        <div
          className="result-question-strip"
          aria-label="Chọn câu hỏi để xem lại"
        >
          {reviewItems.map((item) => (
            <button
              key={item.index}
              className={`result-question-tab${
                item.index === selectedReviewIndex ? " active" : ""
              }${item.isCorrect ? " correct" : " needs-review"}`}
              type="button"
              onClick={() => setSelectedReviewIndex(item.index)}
              aria-pressed={item.index === selectedReviewIndex}
            >
              <span>Câu {item.index + 1}</span>
              <strong>{item.isCorrect ? "Đạt" : "Cần xem lại"}</strong>
            </button>
          ))}
        </div>

        {selectedReview && (
          <div className="info-block result-review-panel">
            <h3>
              {selectedReview.isCorrect ? "Đạt" : "Cần xem lại"} - Câu{" "}
              {selectedReview.index + 1}
            </h3>
            {selectedReview.isOpen ? (
              <dl className="open-grade-summary">
                <div className="open-grade-row">
                  <dt>Câu trả lời của bạn</dt>
                  <dd>{selectedReview.answerText}</dd>
                </div>
                <div className="open-grade-row">
                  <dt>Đạt hay chưa đạt</dt>
                  <dd>{selectedReview.gradeText}</dd>
                </div>
                <div className="open-grade-row">
                  <dt>Lý do</dt>
                  <dd>{selectedReview.gradeReason}</dd>
                </div>
              </dl>
            ) : (
              <>
                <p>
                  <strong>{selectedReview.question.text}</strong>
                </p>
                <ul
                  className="answer-review-options"
                  aria-label={`Các lựa chọn câu ${selectedReview.index + 1}`}
                >
                  {selectedReview.question.options.map((option, optionIndex) => {
                    const letter = String.fromCharCode(65 + optionIndex);
                    const pickedOption =
                      selectedReview.pickedIndex === optionIndex;
                    const correctOption =
                      selectedReview.correctIndex === optionIndex;
                    const stateClass = correctOption
                      ? " correct"
                      : pickedOption
                        ? " picked-wrong"
                        : "";
                    const optionLabels = [
                      `Lựa chọn ${letter}: ${option}`,
                      pickedOption ? "Bạn chọn" : null,
                      correctOption ? "Đáp án đúng" : null,
                    ]
                      .filter(Boolean)
                      .join(". ");

                    return (
                      <li
                        key={optionIndex}
                        className={`answer-review-option${stateClass}`}
                        aria-label={optionLabels}
                      >
                        <strong>{letter}</strong>
                        <span className="answer-review-text">{option}</span>
                        <span className="answer-review-badges">
                          {pickedOption && (
                            <span className="answer-review-badge picked">
                              Bạn chọn
                            </span>
                          )}
                          {correctOption && (
                            <span className="answer-review-badge correct">
                              <CheckCircle size={14} aria-hidden="true" />
                              Đúng
                            </span>
                          )}
                        </span>
                      </li>
                    );
                  })}
                </ul>
                {selectedReview.question.explanation && (
                  <p className="answer-review-note">
                    {selectedReview.question.explanation}
                  </p>
                )}
                {selectedReview.question.evidence && (
                  <p className="answer-review-evidence">
                    Dẫn chứng: {selectedReview.question.evidence}
                  </p>
                )}
              </>
            )}
          </div>
        )}

        <div className="actions-row result-actions">
          {onContinue && result.passed ? (
            <button className="btn primary" type="button" onClick={onContinue}>
              {unlockedLevel ? `Tiếp tục Level ${unlockedLevel}` : "Tiếp tục"}
            </button>
          ) : (
            <Link className="btn primary" to="/leaderboard">
              Xem bảng xếp hạng
            </Link>
          )}
          <Link
            className="btn secondary"
            to={`/characters/${character.id}/chat`}
          >
            Quay lại trò chuyện
          </Link>
          <button className="btn ghost" onClick={onRetry}>
            Làm lại
          </button>
        </div>
      </div>
    </section>
  );
}

export default function Challenge() {
  const { id } = useParams<{ id: string }>();
  const matches = useAppStore((s) => s.matches);
  const completed = useAppStore((s) => s.completed);
  const levelResults = useAppStore((s) => s.levelResults);
  const retryChallenge = useAppStore((s) => s.retryChallenge);
  const saveLevelChallenge = useAppStore((s) => s.saveLevelChallenge);
  const retryLevelChallenge = useAppStore((s) => s.retryLevelChallenge);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data: character, isLoading } = useCharacter(id);
  const submit = useSubmitChallengeMutation();

  const [activeQuestion, setActiveQuestion] = useState(0);
  const [answers, setAnswers] = useState<AnswerValue[]>([]);
  const [recentLevelResult, setRecentLevelResult] = useState<{
    challenge: CharacterLevelChallenge;
    result: ChallengeResult;
  } | null>(null);
  const [isGradingOpenAnswer, setIsGradingOpenAnswer] = useState(false);
  const [gradeError, setGradeError] = useState<string | null>(null);
  const [levelUpView, setLevelUpView] = useState<{
    completed: 1 | 2 | 3;
    unlocked: 2 | 3;
  } | null>(null);

  const activeLevel = useMemo(
    () => (character ? getActiveChallengeLevel(character, levelResults) : 1),
    [character, levelResults],
  );
  const levelChallenge = character?.levelChallenges?.find(
    (challenge) => challenge.level === activeLevel,
  );

  useEffect(() => {
    setActiveQuestion(0);
    setAnswers([]);
    setRecentLevelResult(null);
    setGradeError(null);
    setLevelUpView(null);
  }, [id]);

  if (!id) return <Navigate to="/discover" replace />;
  if (isLoading) return null;
  if (!character || !matches.includes(id)) {
    return (
      <section className="page narrow">
        <div className="card empty-state">
          <h1 className="headline-lg">Chưa mở khóa thử thách</h1>
          <p className="lead">
            Bạn cần chọn nhân vật trong màn Khám phá trước khi làm thử thách.
          </p>
          <Link className="btn primary" to="/discover">
            Quay lại Khám phá
          </Link>
        </div>
      </section>
    );
  }

  const recent = recentLevelResult;
  const existingLevelResult =
    character && levelChallenge
      ? getLevelResult(levelResults, character.id, levelChallenge.level)
      : undefined;
  const existing = levelChallenge ? existingLevelResult : completed[id];
  if (recent) {
    const advanceToNextLevel = () => {
      setLevelUpView(null);
      setRecentLevelResult(null);
      setActiveQuestion(0);
      setAnswers([]);
    };
    return (
      <>
        <ResultView
          character={character}
          questions={recent.challenge.questions}
          result={recent.result}
          levelChallenge={recent.challenge}
          levelResults={levelResults}
          onContinue={() => {
            if (recent.result.nextLevelUnlocked) {
              setLevelUpView({
                completed: recent.result.level ?? recent.challenge.level,
                unlocked: recent.result.nextLevelUnlocked,
              });
            } else {
              advanceToNextLevel();
            }
          }}
          onRetry={() => {
            setLevelUpView(null);
            retryLevelChallenge(id, recent.challenge.level);
            setActiveQuestion(0);
            setAnswers([]);
            setRecentLevelResult(null);
          }}
        />
        {levelUpView && (
          <LevelUpOverlay
            character={character}
            completedLevel={levelUpView.completed}
            unlockedLevel={levelUpView.unlocked}
            onContinue={advanceToNextLevel}
          />
        )}
      </>
    );
  }

  if (existing) {
    return (
      <ResultView
        character={character}
        questions={levelChallenge?.questions ?? character.challenge}
        result={existing}
        levelChallenge={levelChallenge}
        levelResults={levelResults}
        onRetry={() => {
          if (levelChallenge) retryLevelChallenge(id, levelChallenge.level);
          else retryChallenge(id);
          setActiveQuestion(0);
          setAnswers([]);
        }}
      />
    );
  }

  const questions = levelChallenge?.questions ?? character.challenge;
  const levelImages = getLevelImages(character, levelResults);
  const activeLevelImage = levelImages[0];
  const activeLevelTitle =
    character.levels?.find((level) => level.level === activeLevel)?.title ??
    levelChallenge?.phaseTitle;
  const challengeBackgroundStyle = activeLevelImage
    ? ({
        "--challenge-bg-image": `url(${activeLevelImage})`,
      } as CSSProperties)
    : undefined;
  const question = questions[activeQuestion];
  const total = questions.length;
  const isLast = activeQuestion === total - 1;
  const selected = answers[activeQuestion];
  const canAdvance = isOpenQuestion(question)
    ? typeof selected === "string" && selected.trim().length > 0
    : selected !== undefined;

  const isAnswered = (q: ChallengeQuestion, index: number): boolean => {
    const value = answers[index];
    return isOpenQuestion(q)
      ? typeof value === "string" && value.trim().length > 0
      : value !== undefined;
  };
  const answeredCount = questions.reduce(
    (count, q, index) => (isAnswered(q, index) ? count + 1 : count),
    0,
  );

  const setAnswer = (answer: AnswerValue) => {
    setGradeError(null);
    setAnswers((prev) => {
      const next = [...prev];
      next[activeQuestion] = answer;
      return next;
    });
  };

  const gradeOpenAnswers = async (
    challenge: CharacterLevelChallenge,
  ): Promise<Record<string, OpenEndedGradeResult>> => {
    const grades: Record<string, OpenEndedGradeResult> = {};
    for (const [index, item] of challenge.questions.entries()) {
      if (!isOpenQuestion(item)) continue;
      const answer = answers[index];
      if (typeof answer !== "string" || !answer.trim()) {
        throw new Error("Câu tự luận cần có nội dung trước khi nộp bài.");
      }
      grades[item.id] = await api.gradeOpenEndedAnswer({
        characterId: character.id,
        characterName: character.name,
        workTitle: character.work,
        phaseTitle: challenge.phaseTitle,
        question: item,
        answer,
      });
    }
    return grades;
  };

  const handleNext = async () => {
    if (!canAdvance) return;
    if (!isLast) {
      setActiveQuestion((q) => q + 1);
      return;
    }
    if (levelChallenge) {
      setIsGradingOpenAnswer(true);
      setGradeError(null);
      try {
        const openGrades = await gradeOpenAnswers(levelChallenge);
        const result = scoreLevelChallenge(levelChallenge, answers, openGrades);
        saveLevelChallenge(id, levelChallenge.level, result);
        try {
          await api.saveProgress(currentProgressSnapshot());
          await queryClient.invalidateQueries({
            queryKey: queryKeys.leaderboard,
          });
        } catch (err) {
          console.warn("level challenge progress save failed", err);
        }
        setRecentLevelResult({ challenge: levelChallenge, result });
      } catch (err) {
        setGradeError(
          err instanceof Error
            ? err.message
            : "Không chấm được câu tự luận. Vui lòng thử lại.",
        );
      } finally {
        setIsGradingOpenAnswer(false);
      }
      return;
    }
    await submit.mutateAsync({ id, answers: answers as number[] });
    navigate(`/characters/${id}/challenge`, { replace: true });
  };

  return (
    <section
      className="reference-challenge challenge-stage"
      style={challengeBackgroundStyle}
    >
      <div className="challenge-stage-art" aria-hidden="true" />
      <div className="challenge-stage-inner">
        <header className="challenge-hero">
          <p className="challenge-eyebrow">Thử thách nhân vật</p>
          <h1 className="headline-lg">{character.name}</h1>
          <div className="challenge-level-strip">
            <p>
              {levelChallenge ? `Level ${levelChallenge.level}` : "Thử thách"}
              {activeLevelTitle ? ` · ${activeLevelTitle}` : ""}
            </p>
            {levelChallenge && (
              <LevelProgress
                character={character}
                levelResults={levelResults}
                compact
                className="challenge-level-progress"
              />
            )}
          </div>
        </header>

        <div
          className="challenge-question-meta"
          aria-label={`Tiến độ câu hỏi: câu ${
            activeQuestion + 1
          } trên ${total}. Đã trả lời ${answeredCount} trên ${total}.`}
        >
          <span>
            Câu {activeQuestion + 1}/{total}
          </span>
          <div className="challenge-progress-top" aria-hidden="true">
            <span
              style={{ width: `${((activeQuestion + 1) / total) * 100}%` }}
            />
          </div>
        </div>

        <div className="challenge-card challenge-question-card card">
          <p className="question">{question.text}</p>
          {isOpenQuestion(question) ? (
            <div className="open-answer-block">
              <textarea
                value={typeof selected === "string" ? selected : ""}
                onChange={(event) => setAnswer(event.target.value)}
                placeholder="Viết câu trả lời 2-3 câu theo hiểu biết của bạn..."
                rows={5}
              />
            </div>
          ) : (
            <div className="info-stack">
              {question.options.map((option, index) => {
                const active = selected === index;
                return (
                  <button
                    key={index}
                    className={`option${active ? " active" : ""}`}
                    onClick={() => setAnswer(index)}
                    type="button"
                  >
                    <strong>{String.fromCharCode(65 + index)}</strong>
                    <span>{option}</span>
                    {active && <CheckCircle size={18} />}
                  </button>
                );
              })}
            </div>
          )}
        </div>
        {gradeError && <p className="form-error">{gradeError}</p>}
        <div className="challenge-actions">
          <button
            className="btn primary"
            type="button"
            disabled={!canAdvance || submit.isPending || isGradingOpenAnswer}
            onClick={handleNext}
          >
            {isGradingOpenAnswer
              ? "Đang chấm..."
              : isLast
                ? "Nộp bài"
                : "Câu tiếp theo"}
          </button>
        </div>
      </div>
    </section>
  );
}
