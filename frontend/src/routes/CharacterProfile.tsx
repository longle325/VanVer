import { Link, Navigate, useParams } from "react-router-dom";
import { ArrowLeft, MapPin, ChevronDown, MessageSquare, BookOpen } from "lucide-react";
import { useCharacter } from "@/api/queries";
import { useAppStore } from "@/stores/useAppStore";
import CharacterArt from "@/components/CharacterArt";
import CharacterVideoPlayer from "@/components/CharacterVideoPlayer";
import VoicePlayButton from "@/components/VoicePlayButton";
import LevelProgress from "@/components/LevelProgress";
import { getLevelImages, getUnlockedCharacterLevel } from "@/lib/characterLevels";
import type { Character } from "@/types";

interface ProfileCopy {
  summary: string;
  bio: string;
  conflict: string;
  traits: string[];
}

const profileCopy: Record<string, ProfileCopy> = {
  "chi-pheo": {
    summary:
      "Một người bị làng Vũ Đại đẩy ra ngoài rìa, vẫn đau đáu muốn được gọi là người lương thiện.",
    bio:
      "Chí trở về làng với men rượu và những vết sẹo, nhưng phía sau vẻ dữ dằn là một đời thèm được thương. Bát cháo hành mở ra cho anh một khoảnh khắc rất người.",
    conflict:
      "Bi kịch của Chí nằm giữa phần lương thiện vừa thức dậy và định kiến xã hội không cho anh đường quay về.",
    traits: ["Khao khát", "Tổn thương", "Bộc trực"],
  },
  mi: {
    summary:
      "Một tâm hồn bị nhốt trong căn buồng tối, nhưng tiếng sáo mùa xuân vẫn gọi cô trở lại với đời.",
    bio:
      "Mị từng yêu đời, biết thổi sáo và có quyền mơ về hạnh phúc. Khi bị biến thành con dâu gạt nợ, cô lặng đi, rồi dần tìm lại sức sống của mình.",
    conflict:
      "Bi kịch chính là cuộc giằng co giữa nỗi sợ đã ăn sâu và khát vọng tự do bùng lên khi Mị thấy nỗi đau của A Phủ.",
    traits: ["Lặng lẽ", "Mãnh liệt", "Nhân hậu"],
  },
  "xuan-toc-do": {
    summary:
      "Một kẻ cơ hội bước vào sân khấu thượng lưu và làm lộ ra cả một xã hội mê danh hão.",
    bio:
      "Xuân đi lên bằng may rủi, miệng lưỡi và khả năng bắt chước những vỏ bọc văn minh. Càng được tung hô, anh càng làm tiếng cười trào phúng sắc hơn.",
    conflict:
      "Bi kịch không nằm trong Xuân, mà ở xã hội đã biến một kẻ vô lại thành biểu tượng đáng kính.",
    traits: ["Cơ hội", "Láu cá", "Trào phúng"],
  },
  "luc-van-tien": {
    summary:
      "Một chàng nho sinh giữ nghĩa khí như lời hẹn với chính mình, ngay cả khi đời liên tục thử lòng.",
    bio:
      "Vân Tiên bước ra từ lý tưởng nghĩa hiệp Nam Bộ: gặp việc bất bình thì ra tay, làm ơn mà không đòi báo đáp. Nghịch cảnh chỉ làm rõ thêm khí tiết của chàng.",
    conflict:
      "Bi kịch chính là thử thách giữa chữ hiếu, chí công danh và niềm tin trong sáng liên tục bị phản bội.",
    traits: ["Trượng nghĩa", "Hiếu thảo", "Thủy chung"],
  },
  "thuy-kieu": {
    summary:
      "Một tâm hồn tài hoa đang chọn chữ hiếu, giữ chữ tình, và đi qua định mệnh bằng lòng tự trọng.",
    bio:
      "Kiều bước vào đời với tài đàn, sắc đẹp và một tình yêu vừa chớm. Gia biến buộc nàng tự bán mình cứu cha, mở đầu mười lăm năm lưu lạc.",
    conflict:
      "Bi kịch của Kiều nằm giữa chữ hiếu với gia đình, chữ tình với Kim Trọng và một số phận luôn bị đồng tiền, quyền lực xô đẩy.",
    traits: ["Hiếu thảo", "Đa cảm", "Tự trọng"],
  },
};

const ctaNames: Record<string, string> = {
  "chi-pheo": "Chí",
  mi: "Mị",
  "xuan-toc-do": "Xuân",
  "luc-van-tien": "Vân Tiên",
  "thuy-kieu": "Kiều",
};

function splitTraits(personality: string): string[] {
  return personality
    .split(/[,;]/)
    .map((t) => t.trim())
    .filter(Boolean);
}

function getPortrait(character: Character): string | undefined {
  return character.portrait || character.images?.[0] || character.image;
}

function sentencePreview(text: string, maxSentences = 2): string {
  const sentences = text
    .split(/(?<=[.!?。])\s+/)
    .map((sentence) => sentence.trim())
    .filter(Boolean);

  if (sentences.length === 0) return text;
  return sentences.slice(0, maxSentences).join(" ");
}

function getProfileCopy(character: Character): ProfileCopy {
  return (
    profileCopy[character.id] ?? {
      summary: sentencePreview(character.bio, 1),
      bio: sentencePreview(character.bio, 2),
      conflict: sentencePreview(character.conflict, 1),
      traits: splitTraits(character.personality).slice(0, 3),
    }
  );
}

function formatGenre(genre?: string): string | undefined {
  if (!genre) return undefined;
  if (genre.toLowerCase() === "truyện thơ nôm") return "Truyện thơ Nôm";
  return genre;
}

function getCtaName(character: Character): string {
  return ctaNames[character.id] ?? character.name;
}

export default function CharacterProfile() {
  const { id = "" } = useParams<{ id: string }>();
  const { data: character, isLoading, isError } = useCharacter(id);
  const matches = useAppStore((s) => s.matches);
  const completed = useAppStore((s) => s.completed);
  const levelResults = useAppStore((s) => s.levelResults);

  if (isLoading) {
    return (
      <section className="page narrow">
        <div className="card empty-state">
          <p className="lead">Đang tải hồ sơ nhân vật...</p>
        </div>
      </section>
    );
  }

  if (isError || !character) {
    return <Navigate to="/collection" replace />;
  }

  const levelImages = getLevelImages(character, levelResults);
  const portrait = character.portrait || levelImages[0] || getPortrait(character);
  const unlockedLevel = getUnlockedCharacterLevel(character, levelResults);
  const copy = getProfileCopy(character);
  const genre = formatGenre(character.genre);
  const isMatched = matches.includes(character.id);
  const result = completed[character.id];

  return (
    <section className="page narrow reference-character-profile">
      <Link to="/collection" className="btn ghost back-link">
        <ArrowLeft size={18} />
        Bộ sưu tập
      </Link>

      <article className="card character-profile">
        <div className="character-profile-hero">
          <div className="character-profile-portrait">
            {portrait ? (
              <img src={portrait} alt={character.name} />
            ) : (
              <CharacterArt character={character} />
            )}
          </div>

          <div className="character-profile-heading">
            <p className="kicker">
              {genre ? `${genre} · ` : ""}
              {character.work} · {character.author}
            </p>
            <h1 className="headline-lg">{character.name}</h1>
            {character.levelChallenges?.length ? (
              <p className="profile-location">
                <BookOpen size={14} />
                Level {unlockedLevel}:{" "}
                {character.levels?.find((level) => level.level === unlockedLevel)
                  ?.title ?? "Giai đoạn hiện tại"}
              </p>
            ) : null}
            {character.artTitle && (
              <p className="profile-location">
                <MapPin size={14} />
                Đang ở {character.artTitle}
              </p>
            )}
            <p className="profile-summary">{copy.summary}</p>
          </div>
        </div>

        {character.levelChallenges?.length ? (
          <LevelProgress
            character={character}
            levelResults={levelResults}
            className="profile-level-progress"
          />
        ) : null}

        <div className="quote-row profile-quote-card">
          <blockquote className="quote profile-quote">
            "{character.quote}"
          </blockquote>
          <VoicePlayButton characterId={character.id} />
        </div>

        <div className="character-profile-grid">
          <section className="profile-section">
            <h2>Tiểu sử</h2>
            <p>{copy.bio}</p>
          </section>

          <section className="profile-section profile-section-featured">
            <h2>Bi kịch chính</h2>
            <p>{copy.conflict}</p>
          </section>

          <section className="profile-section">
            <h2>Tính cách</h2>
            <div className="trait-row profile-traits">
              {copy.traits.map((trait) => (
                <span key={trait}>{trait}</span>
              ))}
            </div>
          </section>
        </div>

        <details className="profile-analysis">
          <summary>
            <span>Mở rộng phân tích</span>
            <ChevronDown size={18} />
          </summary>

          <div className="profile-analysis-grid">
            {character.context && (
              <section className="profile-section">
                <h2>Bối cảnh</h2>
                <p>{character.context}</p>
              </section>
            )}

            {character.voice && (
              <section className="profile-section">
                <h2>Chất giọng</h2>
                <p>{character.voice}</p>
              </section>
            )}

            {character.sources && character.sources.length > 0 && (
              <section className="profile-section">
                <h2>Chi tiết then chốt</h2>
                <ul className="profile-sources">
                  {character.sources.map((source) => (
                    <li key={source}>{source}</li>
                  ))}
                </ul>
              </section>
            )}

            {character.interpretationThemes &&
              character.interpretationThemes.length > 0 && (
                <section className="profile-section">
                  <h2>Chủ đề diễn giải</h2>
                  <div className="trait-row profile-analysis-tags">
                    {character.interpretationThemes.map((theme) => (
                      <span key={theme}>{theme}</span>
                    ))}
                  </div>
                </section>
              )}

            {character.symbols && character.symbols.length > 0 && (
              <section className="profile-section">
                <h2>Biểu tượng</h2>
                <div className="trait-row profile-analysis-tags">
                  {character.symbols.map((symbol) => (
                    <span key={symbol}>{symbol}</span>
                  ))}
                </div>
              </section>
            )}
          </div>
        </details>

        {character.videos?.[0] && (
          <section className="profile-video-section">
            <h2>Video hành trình nhân vật</h2>
            <div className="profile-video-frame">
              <CharacterVideoPlayer video={character.videos[0]} />
            </div>
            <div className="profile-video-copy">
              <strong>{character.videos[0].title}</strong>
              {character.videos[0].description && (
                <p>{character.videos[0].description}</p>
              )}
            </div>
          </section>
        )}

        <div className="actions-row character-profile-actions">
          <Link
            className="btn primary"
            to={`/characters/${character.id}/chat`}
          >
            <MessageSquare size={18} />
            Trò chuyện với {getCtaName(character)}
          </Link>
          <Link
            className="btn secondary"
            to={`/characters/${character.id}/challenge`}
          >
            <BookOpen size={18} />
            Khám phá thử thách
          </Link>
          {(isMatched || result) && (
            <p className="profile-progress-note">
              {result
                ? `Lần thử gần nhất: ${result.score}/5 · +${result.awarded} điểm`
                : "Đã có trong bộ sưu tập của bạn"}
            </p>
          )}
        </div>
      </article>
    </section>
  );
}
