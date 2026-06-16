export interface MusicTrack {
  id: "vet-muc-tren-giay" | "duoi-anh-den-dau" | "across-the-jade-valley";
  title: string;
  mood: string;
  src: string;
}

export const CHALLENGE_MUSIC_TRACK: MusicTrack = {
  id: "across-the-jade-valley",
  title: "Across the Jade Valley",
  mood: "Tươi sáng, cổ trang — đàn gảy nhanh và nhịp trống nhẹ",
  src: "/audio/across-the-jade-valley.mp3",
};

export const MUSIC_TRACKS: MusicTrack[] = [
  {
    id: "duoi-anh-den-dau",
    title: "Dưới ánh đèn dầu",
    mood: "Ấm áp, hoài niệm — gõ mõ nhẹ giữa nhịp",
    src: "/audio/duoi-anh-den-dau.mp3",
  },
  {
    id: "vet-muc-tren-giay",
    title: "Vệt mực trên giấy",
    mood: "Trầm tĩnh, thiền định — đàn tranh dẫn dắt",
    src: "/audio/vet-muc-tren-giay.mp3",
  },
];

export const MUSIC_LIBRARY: MusicTrack[] = [
  ...MUSIC_TRACKS,
  CHALLENGE_MUSIC_TRACK,
];

export const DEFAULT_TRACK_ID: MusicTrack["id"] = "duoi-anh-den-dau";
