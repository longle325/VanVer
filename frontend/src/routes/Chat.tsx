import { useEffect, useMemo, useRef, useState } from "react";
import { Link, Navigate, useParams } from "react-router-dom";
import { BookOpen, Send, Sparkles, Pencil, AlertCircle } from "lucide-react";
import { useCharacter } from "@/api/queries";
import { api, ApiError } from "@/api/client";
import { useAppStore } from "@/stores/useAppStore";
import { getLevelImages } from "@/lib/characterLevels";
import type { Character, ChatMessage, ChatSource } from "@/types";

const defaultOpening = (character: Character) =>
  `Tôi là ${character.name}. Hãy hỏi tôi về một biểu tượng, xung đột hoặc lựa chọn khiến nhân vật trong ${character.work} trở nên đáng suy nghĩ.`;

const legacyOpening = (character: Character) =>
  `Chào bạn. Tôi là ${character.name}. Bạn có thể hỏi về động cơ, mâu thuẫn, bối cảnh xã hội hoặc một chi tiết trong tác phẩm.`;

const getCharacterImage = (character: Character) =>
  character.avatar || character.images?.[0] || character.image;

function CharacterProfileCard({ character }: { character: Character }) {
  return (
    <div className="character-profile-card" aria-label="Tác phẩm">
      <BookOpen size={20} strokeWidth={1.8} />
      <span>
        <strong>{character.work}</strong>
        <small>{character.author}</small>
      </span>
    </div>
  );
}

function ChatHeader({ character }: { character: Character }) {
  const chatImage = getCharacterImage(character);

  return (
    <header className="chat-header">
      <div className="chat-identity">
        {chatImage ? (
          <img
            className="avatar image-avatar"
            src={chatImage}
            alt={character.name}
          />
        ) : (
          <div
            className="avatar"
            style={
              {
                "--art-a": character.artA,
                "--art-b": character.artB,
              } as React.CSSProperties
            }
          >
            {character.initial}
          </div>
        )}
        <div>
          <h1>{character.name}</h1>
          <p>
            <span className="online-dot" />
            Đang trò chuyện
          </p>
        </div>
      </div>
      <CharacterProfileCard character={character} />
    </header>
  );
}

function CharacterMessage({
  message,
  character,
}: {
  message: ChatMessage;
  character: Character;
}) {
  if (message.from === "user") {
    return (
      <div className="message-row user">
        <div className="message user">{message.text}</div>
      </div>
    );
  }
  const avatarImage = getCharacterImage(character);
  const avatar = avatarImage ? (
    <img className="message-avatar" src={avatarImage} alt={character.name} />
  ) : (
    <span className="message-avatar fallback">{character.initial}</span>
  );
  return (
    <div className="message-row bot">
      {avatar}
      <div className="message bot">
        {message.text}
        {message.sources && message.sources.length > 0 && (
          <ChatSourceChips sources={message.sources} />
        )}
      </div>
    </div>
  );
}

function ThinkingBubble({ character }: { character: Character }) {
  const avatarImage = getCharacterImage(character);
  const avatar = avatarImage ? (
    <img className="message-avatar" src={avatarImage} alt={character.name} />
  ) : (
    <span className="message-avatar fallback">{character.initial}</span>
  );
  return (
    <div
      className="message-row bot"
      role="status"
      aria-live="polite"
      aria-label={`${character.name} đang soạn câu trả lời`}
    >
      {avatar}
      <div className="message bot typing-bubble">
        <span className="typing-bubble-dot" />
        <span className="typing-bubble-dot" />
        <span className="typing-bubble-dot" />
      </div>
    </div>
  );
}

function ChatSourceChips({ sources }: { sources: ChatSource[] }) {
  // De-duplicate by title so the same work doesn't render twice when the
  // retriever surfaces multiple chunks from one document.
  const seen = new Set<string>();
  const unique: ChatSource[] = [];
  for (const s of sources) {
    if (seen.has(s.title)) continue;
    seen.add(s.title);
    unique.push(s);
  }
  return (
    <ul className="chat-sources" aria-label="Nguồn dẫn">
      {unique.map((source, index) => (
        <li key={`${source.title}-${index}`} className="chat-source-chip">
          <span className="chat-source-title">{source.title}</span>
          {source.snippet && (
            <span className="chat-source-snippet">{source.snippet}</span>
          )}
        </li>
      ))}
    </ul>
  );
}

function SuggestedQuestionChips({
  prompts,
  onSelect,
}: {
  prompts: string[];
  onSelect: (prompt: string) => void;
}) {
  if (!prompts.length) return null;

  return (
    <div className="quick-row" aria-label="Câu hỏi gợi ý">
      {prompts.map((prompt) => (
        <button
          key={prompt}
          className="chip literary-chip"
          type="button"
          onClick={() => onSelect(prompt)}
        >
          {prompt}
        </button>
      ))}
    </div>
  );
}

function ChatInput({
  characterId,
  character,
  draft,
  streaming,
  awaiting,
  suggestedQuestions,
  onDraftChange,
  onPromptSelect,
  onSubmit,
}: {
  characterId: string;
  character: Character;
  draft: string;
  streaming: string;
  awaiting: boolean;
  suggestedQuestions: string[];
  onDraftChange: (draft: string) => void;
  onPromptSelect: (prompt: string) => void;
  onSubmit: (event: React.FormEvent) => void;
}) {
  const handleTextAreaKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Guard against the dupe-message bug with Vietnamese IME (macOS, Telex,
    // Bộ gõ tiếng Việt, etc.): when the user finalises a tone-marked word
    // and presses Enter, the browser fires *two* keydown events — one from
    // compositionend (which has `isComposing = true` or `keyCode === 229`)
    // and a real one. Without this guard, the first call submits the full
    // draft and the second submits the trailing word residue.
    if (
      event.key !== "Enter" ||
      event.shiftKey ||
      event.nativeEvent.isComposing ||
      event.keyCode === 229
    ) {
      return;
    }
    event.preventDefault();
    onSubmit(event);
  };

  return (
    <form className="chat-form literary-chat-form" onSubmit={onSubmit}>
      <SuggestedQuestionChips
        prompts={suggestedQuestions}
        onSelect={onPromptSelect}
      />
      <textarea
        value={draft}
        onChange={(e) => onDraftChange(e.target.value)}
        onKeyDown={handleTextAreaKeyDown}
        autoComplete="off"
        rows={2}
        placeholder={`Hỏi ${character.name} về bi kịch, biểu tượng, mâu thuẫn...`}
      />
      <Link
        className="btn secondary deeper-button"
        to={`/characters/${characterId}/challenge`}
        aria-label="Mở trang thử thách 5 câu"
      >
        <Sparkles size={19} strokeWidth={1.8} />
        Làm thử thách
      </Link>
      <button
        className="btn ghost send-button"
        type="submit"
        disabled={!!streaming || awaiting || !draft.trim()}
      >
        <Send size={17} strokeWidth={1.8} />
        Gửi
      </button>
    </form>
  );
}

function ThemeTags({
  themes,
  character,
  onSelect,
}: {
  themes: string[];
  character: Character;
  onSelect: (prompt: string) => void;
}) {
  return (
    <div className="theme-tags">
      {themes.map((theme) => (
        <button
          key={theme}
          type="button"
          onClick={() =>
            onSelect(`${theme} được thể hiện như thế nào trong ${character.work}?`)
          }
        >
          {theme}
        </button>
      ))}
    </div>
  );
}

function SymbolList({
  symbols,
  character,
  onSelect,
}: {
  symbols: string[];
  character: Character;
  onSelect: (prompt: string) => void;
}) {
  return (
    <div className="symbol-list">
      {symbols.map((symbol) => (
        <button
          key={symbol}
          type="button"
          onClick={() =>
            onSelect(`${symbol} có vai trò gì trong bi kịch của ${character.name}?`)
          }
        >
          <span>{symbol}</span>
        </button>
      ))}
    </div>
  );
}

const SYMBOL_PHRASE_STOPS = [
  " có ",
  " của ",
  " khiến ",
  " khơi ",
  " thể hiện ",
  " cho thấy ",
  " là ",
  " đi cùng ",
  " dùng ",
  " được ",
  " nhắm ",
];

function deriveSymbolFromSource(source: string): string {
  const sentence = source.replace(/[.!?].*$/, "").trim();
  const stopIndex = SYMBOL_PHRASE_STOPS
    .map((stop) => sentence.indexOf(stop))
    .filter((index) => index > 0)
    .sort((a, b) => a - b)[0];

  const phrase = stopIndex ? sentence.slice(0, stopIndex).trim() : sentence;
  const words = phrase.split(/\s+/).filter(Boolean);
  if (words.length <= 5) return phrase;
  return `${words.slice(0, 5).join(" ")}...`;
}

function InsightPanel({
  character,
  onSelect,
}: {
  character: Character;
  onSelect: (prompt: string) => void;
}) {
  const themes = character.interpretationThemes ?? [
    character.conflict.split(";")[0],
  ];
  const symbols =
    character.symbols ?? character.sources.map(deriveSymbolFromSource);

  return (
    <aside className="panel source-panel insight-panel">
      <section>
        <h2>Chủ đề nên khám phá</h2>
        <ThemeTags
          themes={themes}
          character={character}
          onSelect={onSelect}
        />
      </section>
      <section>
        <h2>Biểu tượng quan trọng</h2>
        <SymbolList
          symbols={symbols}
          character={character}
          onSelect={onSelect}
        />
      </section>
    </aside>
  );
}

export default function Chat() {
  const { id } = useParams<{ id: string }>();
  const matches = useAppStore((s) => s.matches);
  const chats = useAppStore((s) => s.chats);
  const appendChat = useAppStore((s) => s.appendChat);
  const setChat = useAppStore((s) => s.setChat);
  const removeMatch = useAppStore((s) => s.removeMatch);
  const levelResults = useAppStore((s) => s.levelResults);
  const { data: character, isLoading } = useCharacter(id);
  const displayCharacter = useMemo(() => {
    if (!character) return undefined;
    const images = getLevelImages(character, levelResults);
    return images.length
      ? { ...character, image: images[0], images }
      : character;
  }, [character, levelResults]);

  // Rehydrate chat history from the backend on mount. Mock returns [] so
  // existing local-only state is left untouched.
  //
  // Race guard: if the user types and submits a message before the history
  // request resolves, `appendChat` has already updated the store. Don't
  // clobber that local progress — only replace when the local thread is
  // still empty.
  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    api.getChatHistory(id).then(
      (history) => {
        if (cancelled || history.length === 0) return;
        const localCount =
          useAppStore.getState().chats[id]?.length ?? 0;
        if (localCount > 0) return;
        setChat(id, history);
      },
      (err) => {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 403) {
          // Stale local match — heal immediately so LockedView renders
          // instead of letting the user type a question that's about to
          // 403 the stream call.
          removeMatch(id);
          return;
        }
        // Other errors (backend down, chat flag off): fall back to local.
      },
    );
    return () => {
      cancelled = true;
    };
  }, [id, setChat, removeMatch]);

  const [draft, setDraft] = useState("");
  const [streaming, setStreaming] = useState("");
  const [awaiting, setAwaiting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const threadRef = useRef<HTMLDivElement | null>(null);

  const initialMessage: ChatMessage | null = character
    ? {
        from: "bot",
        text: character.chatOpening ?? defaultOpening(character),
      }
    : null;
  const storedMessages = id ? chats[id] ?? [] : [];
  const messages: ChatMessage[] =
    character && initialMessage
      ? storedMessages.length
        ? storedMessages.map((message, index) =>
            index === 0 &&
            message.from === "bot" &&
            message.text === legacyOpening(character)
              ? initialMessage
              : message,
          )
        : [initialMessage]
      : [];

  useEffect(() => {
    threadRef.current?.scrollTo({
      top: threadRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages.length, streaming, awaiting]);

  if (!id) return <Navigate to="/discover" replace />;
  if (isLoading) return null;
  if (!character || !matches.includes(id)) {
    return (
      <section className="page narrow">
        <div className="card empty-state">
          <h1 className="headline-lg">Chưa mở khóa trò chuyện</h1>
          <p className="lead">
            Bạn cần chọn nhân vật trong màn Khám phá trước khi vào trò chuyện
            hoặc thử thách.
          </p>
          <Link className="btn primary" to="/discover">
            Quay lại Khám phá
          </Link>
        </div>
      </section>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const text = draft.trim();
    if (!text || streaming || awaiting) return;
    setDraft("");
    setError(null);
    appendChat(id, { from: "user", text });

    let buffer = "";
    const sources: ChatSource[] = [];
    setStreaming("");
    setAwaiting(true);
    try {
      for await (const event of api.streamChat({
        characterId: id,
        message: text,
      })) {
        if (event.kind === "token") {
          buffer += event.text;
          setStreaming(buffer);
        } else if (event.kind === "source") {
          sources.push(event.source);
        }
      }
      appendChat(id, {
        from: "bot",
        text: buffer,
        sources: sources.length ? sources : undefined,
      });
    } catch (err) {
      console.error("chat stream failed", err);
      if (err instanceof ApiError && err.status === 403) {
        // Backend says the user hasn't actually matched this character.
        // Local matches are stale — drop the entry and let the route's
        // match guard render the LockedView on the next render.
        removeMatch(id);
        return;
      }
      if (buffer) {
        appendChat(id, {
          from: "bot",
          text: buffer,
          sources: sources.length ? sources : undefined,
        });
      }
      setError(
        "Không tạo được phản hồi. Vui lòng kiểm tra kết nối và thử lại.",
      );
    } finally {
      setStreaming("");
      setAwaiting(false);
    }
  };

  const suggestedQuestions =
    character.suggestedQuestions ?? character.challenge.slice(0, 3).map((q) => q.text);

  return (
    <section className="page chat-layout reference-chat">
      <div className="chat-card">
        <ChatHeader character={displayCharacter ?? character} />
        <div className="chat-thread" ref={threadRef}>
          {messages.map((message, index) => (
            <CharacterMessage
              key={index}
              message={message}
              character={displayCharacter ?? character}
            />
          ))}
          {streaming && (
            <CharacterMessage
              message={{ from: "bot", text: streaming }}
              character={displayCharacter ?? character}
            />
          )}
          {awaiting && !streaming && (
            <ThinkingBubble character={displayCharacter ?? character} />
          )}
          {(streaming || awaiting) && (
            <div className="typing-line">
              <Pencil size={14} />
              {character.name} đang suy ngẫm...
            </div>
          )}
          {error && !streaming && !awaiting && (
            <div className="chat-error" role="alert">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}
        </div>
        <ChatInput
          characterId={id}
          character={character}
          draft={draft}
          streaming={streaming}
          awaiting={awaiting}
          suggestedQuestions={suggestedQuestions}
          onDraftChange={setDraft}
          onPromptSelect={setDraft}
          onSubmit={handleSubmit}
        />
      </div>
      <InsightPanel character={character} onSelect={setDraft} />
    </section>
  );
}
