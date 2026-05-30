import type { CharacterVideo } from "@/types";

interface CharacterVideoSeed {
  id: string;
  name: string;
  work: string;
  image?: string;
  images?: string[];
}

interface CharacterVideoManifestEntry {
  captions?: boolean;
  description?: string;
  title?: string;
}

const characterVideoManifest: Record<string, CharacterVideoManifestEntry> = {
  "chi-dau": {
    captions: true,
    description:
      "Ba chặng của Chị Dậu: giữ chồng con trong mùa sưu, vùng lên trước cai lệ, và chạy qua đêm tối của thân phận người nghèo.",
  },
  "lao-hac": {
    captions: true,
    description:
      "Ba chặng của Lão Hạc: tình thương với cậu Vàng, nỗi day dứt sau khi bán chó, và quyết tâm giữ mảnh vườn cho con.",
  },
  mi: {
    description:
      "Ba chặng chuyển biến của Mị: tiếng sáo tuổi trẻ, đời con dâu gạt nợ, và khoảnh khắc cắt dây cứu A Phủ.",
  },
};

function videoBasePath(characterId: string): string {
  return `/character-videos/${characterId}/${characterId}-three-phase-demo`;
}

function defaultVideoTitle(character: CharacterVideoSeed): string {
  return `Hành trình ba giai đoạn của ${character.name}`;
}

function defaultVideoDescription(character: CharacterVideoSeed): string {
  return `Video preview ba giai đoạn của ${character.name} trong ${character.work}.`;
}

export function hasCharacterVideo(characterId: string): boolean {
  return characterId in characterVideoManifest;
}

export function buildCharacterVideos(
  character: CharacterVideoSeed,
): CharacterVideo[] {
  const entry = characterVideoManifest[character.id];
  if (!entry) return [];

  const basePath = videoBasePath(character.id);
  return [
    {
      id: "three-phase-demo",
      title: entry.title ?? defaultVideoTitle(character),
      src: `${basePath}.mp4`,
      poster: character.images?.[0] ?? character.image,
      captions: entry.captions ? `${basePath}.vtt` : undefined,
      description: entry.description ?? defaultVideoDescription(character),
    },
  ];
}
