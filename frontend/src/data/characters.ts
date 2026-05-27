import type { Character, ChallengeQuestion, CharacterLevel } from "@/types";

// Question id is auto-generated below, so the seed data only supplies
// the substantive fields. This mirrors the wire shape from
// docs/API.md §5.2 once the backend ships.
type SeedChallengeQuestion = Omit<ChallengeQuestion, "id">;
type SeedCharacter = Omit<Character, "challenge"> & {
  challenge: SeedChallengeQuestion[];
};

const q = (
  text: string,
  options: string[],
  answer: number,
  explanation: string,
): SeedChallengeQuestion => ({ text, options, answer, explanation });

type CharacterLevelPlan = Omit<
  CharacterLevel,
  "image" | "images" | "referenceImage" | "referenceImages" | "assetStatus"
>;

const imagesPerLevel = 3;

const visualUpgradeTreatment: Record<CharacterLevel["level"], string> = {
  1: "Level 1 depicts the character's first planned story phase with restrained composition and clear canonical setting.",
  2: "Level 2 depicts the character's second planned story phase with visibly changed context, stronger narrative tension, and phase-specific symbols.",
  3: "Level 3 depicts the character's third planned story phase with the highest emotional stakes, strongest symbolic props, and a clearly distinct canonical setting.",
};

function plannedLevelImages(characterId: string, level: 2 | 3): string[] {
  return Array.from(
    { length: imagesPerLevel },
    (_, index) => `/characters/${characterId}-level-${level}-${index + 1}.png`,
  );
}

const levelPlans: Record<string, CharacterLevelPlan[]> = {
  "chi-pheo": [
    {
      level: 1,
      title: "Canh điền lương thiện",
      unlockRequirement: "Mở khóa khi gặp nhân vật lần đầu.",
      promptFocus:
        "Gợi phần người còn nguyên vẹn trước khi bị nhà tù và cường hào tha hóa.",
      visualPrompt:
        "Chí Phèo thời còn là anh canh điền nghèo, mộc mạc giữa làng Vũ Đại, chưa có vết sẹo dữ dằn hay men rượu phủ đời.",
    },
    {
      level: 2,
      title: "Tha hóa sau nhà tù",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách cơ bản.",
      promptFocus:
        "Nhấn mạnh dáng vẻ dữ dằn, say rượu, bị xã hội biến thành công cụ đe dọa.",
      visualPrompt:
        "Chí Phèo trở về làng Vũ Đại sau nhà tù, mặt đầy sẹo, chai rượu trong tay, dáng đi xiêu vẹo và ánh mắt bị ruồng bỏ.",
    },
    {
      level: 3,
      title: "Câu hỏi quyền làm người",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách nâng cao.",
      promptFocus:
        "Đẩy bi kịch bị cự tuyệt quyền làm người lên cao, không tiết lộ tương lai nếu chưa đúng timeline.",
      visualPrompt:
        "Chí Phèo sau bát cháo hành, đứng trước ngõ nhà Bá Kiến với ánh mắt đau đớn, tỉnh thức và phẫn uất vì đường về lương thiện bị chặn.",
    },
  ],
  mi: [
    {
      level: 1,
      title: "Tiếng sáo tuổi trẻ",
      unlockRequirement: "Mở khóa khi gặp nhân vật lần đầu.",
      promptFocus:
        "Giữ sức sống tuổi trẻ, vẻ đẹp Hmong, tài thổi sáo và tình yêu trước khi bị vùi lấp.",
      visualPrompt:
        "Mị thời trẻ ở miền núi Tây Bắc, mặc váy áo Hmong, thổi sáo giữa mùa xuân và còn ánh nhìn tự do.",
    },
    {
      level: 2,
      title: "Con dâu gạt nợ",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách cơ bản.",
      promptFocus:
        "Tập trung vào sức sống bị giam hãm nhưng trỗi dậy trong đêm tình mùa xuân.",
      visualPrompt:
        "Mị trong nhà thống lí Pá Tra, căn buồng tối và dây trói của A Sử đối lập với tiếng sáo, men rượu và sắc xuân ngoài kia.",
    },
    {
      level: 3,
      title: "Người tự cởi trói",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách nâng cao.",
      promptFocus:
        "Thể hiện lòng thương người chuyển thành hành động phản kháng và tự giải phóng.",
      visualPrompt:
        "Mị trong đêm đông, ánh lửa bếp soi giọt nước mắt A Phủ và khoảnh khắc quyết tâm cắt dây trói để chạy theo con đường sống.",
    },
  ],
  "xuan-toc-do": [
    {
      level: 1,
      title: "Thằng nhặt bóng gặp thời",
      unlockRequirement: "Mở khóa khi gặp nhân vật lần đầu.",
      promptFocus: "Giữ giọng láu cá, đường phố, cơ hội và vô học.",
      visualPrompt:
        "Xuân Tóc Đỏ lang thang sân quần vợt, tóc đỏ nổi bật và vẻ mặt lém lỉnh.",
    },
    {
      level: 2,
      title: "Đốc tờ của xã hội Âu hóa",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách cơ bản.",
      promptFocus:
        "Nhấn mạnh xã hội thượng lưu giả trá biến sự ngu dốt thành danh vọng.",
      visualPrompt:
        "Xuân mặc đồ tây kệch cỡm giữa salon Âu hóa và những ánh nhìn tán tụng.",
    },
    {
      level: 3,
      title: "Anh hùng trào phúng",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách nâng cao.",
      promptFocus:
        "Đẩy chất đại ngôn, lố bịch và nghịch lý xã hội tôn vinh kẻ vô lại.",
      visualPrompt:
        "Xuân diễn thuyết trước đám đông, hào quang giả tạo pha tiếng cười châm biếm.",
    },
  ],
  "luc-van-tien": [
    {
      level: 1,
      title: "Cứu Kiều Nguyệt Nga",
      unlockRequirement: "Mở khóa khi gặp nhân vật lần đầu.",
      promptFocus:
        "Giữ khí chất trẻ, chính trực, thấy việc nghĩa thì làm; không vẽ mù ở giai đoạn này.",
      visualPrompt:
        "Lục Vân Tiên trẻ trên đường đi thi, mắt sáng, đánh cướp Phong Lai cứu Kiều Nguyệt Nga giữa đường rừng và không cầu báo đáp.",
    },
    {
      level: 2,
      title: "Hoạn nạn mù lòa",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách cơ bản.",
      promptFocus:
        "Nhấn mạnh nghịch cảnh mù lòa, bị phản bội nhưng vẫn giữ đạo nghĩa.",
      visualPrompt:
        "Lục Vân Tiên trong chặng hoạn nạn sau khi bị mù, áo nho sinh sờn cũ, tay dò đường nhưng dáng người vẫn ngay thẳng.",
    },
    {
      level: 3,
      title: "Phẩm hạnh được minh chứng",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách nâng cao.",
      promptFocus:
        "Tập trung vào đạo nghĩa được nhận ra sau nhiều thử thách và trật tự công lý được phục hồi.",
      visualPrompt:
        "Lục Vân Tiên sau thử thách, phẩm hạnh và lòng trung chính được minh chứng trong không khí trang nghiêm của công lý phục hồi.",
    },
  ],
  "thuy-kieu": [
    {
      level: 1,
      title: "Tài sắc đầu đời",
      unlockRequirement: "Mở khóa khi gặp nhân vật lần đầu.",
      promptFocus: "Giữ vẻ đa cảm, tài hoa và ý thức về chữ tài chữ mệnh.",
      visualPrompt:
        "Thúy Kiều bên đàn nguyệt, vẻ đẹp tài sắc trong không gian khuê các.",
    },
    {
      level: 2,
      title: "Trao duyên đứt ruột",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách cơ bản.",
      promptFocus:
        "Nhấn mạnh giằng xé giữa chữ hiếu và chữ tình, lời nói vừa lý trí vừa tan nát.",
      visualPrompt:
        "Kiều trong đêm trao duyên, kỷ vật tình yêu đặt giữa ánh đèn khuya.",
    },
    {
      level: 3,
      title: "Lầu Ngưng Bích cô đơn",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách nâng cao.",
      promptFocus:
        "Tập trung vào tả cảnh ngụ tình, cô đơn, nhớ nhà, nhớ người yêu và dự cảm lưu lạc.",
      visualPrompt:
        "Thúy Kiều ở lầu Ngưng Bích, biển trời mênh mông và tâm trạng buồn trông.",
    },
  ],
  "lao-hac": [
    {
      level: 1,
      title: "Ông lão giữ vườn",
      unlockRequirement: "Mở khóa khi gặp nhân vật lần đầu.",
      promptFocus: "Giữ giọng lễ phép, nghèo khổ, cô độc và thương con.",
      visualPrompt:
        "Lão Hạc bên mảnh vườn cũ, dáng gầy guộc và ánh mắt đợi con.",
    },
    {
      level: 2,
      title: "Nỗi đau cậu Vàng",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách cơ bản.",
      promptFocus:
        "Nhấn mạnh mặc cảm lừa cậu Vàng, nỗi đau đạo đức và sự tự trách.",
      visualPrompt:
        "Lão Hạc sau khi bán cậu Vàng, ngồi bên ông giáo với khuôn mặt mếu xệch.",
    },
    {
      level: 3,
      title: "Lòng tự trọng cuối cùng",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách nâng cao.",
      promptFocus:
        "Tập trung vào quyết tâm không ăn vào tiền của con và bi kịch nhân phẩm.",
      visualPrompt:
        "Lão Hạc trong căn nhà nghèo, tiền ma chay và văn tự mảnh vườn đặt trước mặt.",
    },
  ],
  "chi-dau": [
    {
      level: 1,
      title: "Người đàn bà mùa sưu",
      unlockRequirement: "Mở khóa khi gặp nhân vật lần đầu.",
      promptFocus: "Giữ giọng mộc mạc, tất bật, nhẫn nhục vì chồng con.",
      visualPrompt:
        "Chị Dậu trong căn nhà tranh nghèo, nồi cháo nóng và chồng ốm sau lưng.",
    },
    {
      level: 2,
      title: "Bị dồn đến đường cùng",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách cơ bản.",
      promptFocus:
        "Nhấn mạnh cảnh bán con, bán chó, đói nghèo và tủi nhục đẩy chị vượt quá sức chịu đựng.",
      visualPrompt:
        "Chị Dậu trong áp lực sưu thuế, gương mặt kiệt quệ sau cảnh bán con bán chó, căn nhà nghèo nặng bóng cường hào.",
    },
    {
      level: 3,
      title: "Tức nước vỡ bờ",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách nâng cao.",
      promptFocus:
        "Đẩy sức phản kháng dữ dội nhưng vẫn bắt nguồn từ tình thương gia đình.",
      visualPrompt:
        "Chị Dậu vùng lên giữa căn nhà tối, bóng cường hào bị đẩy lùi.",
    },
  ],
  "ong-sau": [
    {
      level: 1,
      title: "Người cha trở về",
      unlockRequirement: "Mở khóa khi gặp nhân vật lần đầu.",
      promptFocus: "Giữ giọng Nam Bộ chân chất, nôn nóng được con nhận cha.",
      visualPrompt:
        "Ông Sáu về thăm nhà, vết thẹo trên mặt và ánh mắt chờ tiếng gọi ba.",
    },
    {
      level: 2,
      title: "Tiếng ba muộn màng",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách cơ bản.",
      promptFocus:
        "Nhấn mạnh hạnh phúc vỡ òa trong phút chia tay và nỗi đau chiến tranh.",
      visualPrompt:
        "Ông Sáu ôm bé Thu trong khoảnh khắc chia tay, nước mắt và bụi đường.",
    },
    {
      level: 3,
      title: "Chiếc lược ngà",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách nâng cao.",
      promptFocus:
        "Tập trung vào lời hứa, nỗi ân hận và tình cha kết tinh trong kỷ vật.",
      visualPrompt:
        "Ông Sáu tỉ mẩn làm chiếc lược ngà trong căn cứ rừng, ánh lửa nhỏ soi tay.",
    },
  ],
  "ong-hai": [
    {
      level: 1,
      title: "Người khoe làng Chợ Dầu",
      unlockRequirement: "Mở khóa khi gặp nhân vật lần đầu.",
      promptFocus: "Giữ giọng nông dân hồ hởi, thích kể và tự hào về làng.",
      visualPrompt:
        "Ông Hai ở nơi tản cư, hào hứng kể chuyện làng Chợ Dầu với mọi người.",
    },
    {
      level: 2,
      title: "Tin làng theo Tây",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách cơ bản.",
      promptFocus:
        "Nhấn mạnh khủng hoảng xấu hổ, tủi nhục và giằng xé giữa yêu làng, yêu nước.",
      visualPrompt:
        "Ông Hai chết lặng sau khi nghe tin làng theo Tây, chợ tản cư mờ sau lưng.",
    },
    {
      level: 3,
      title: "Làng yêu nước",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách nâng cao.",
      promptFocus:
        "Tập trung vào niềm vui được minh oan, tình yêu làng hòa vào lòng kháng chiến.",
      visualPrompt:
        "Ông Hai vui mừng khoe tin nhà bị đốt mà làng không theo giặc.",
    },
  ],
  "vu-nuong": [
    {
      level: 1,
      title: "Người vợ giữ khuôn phép",
      unlockRequirement: "Mở khóa khi gặp nhân vật lần đầu.",
      promptFocus: "Giữ giọng dịu, trang trọng, thủy chung và hiếu nghĩa.",
      visualPrompt:
        "Vũ Nương tiễn chồng ra trận, dáng thùy mị trong không gian cổ truyền.",
    },
    {
      level: 2,
      title: "Oan khuất chiếc bóng",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách cơ bản.",
      promptFocus:
        "Nhấn mạnh sự bất lực trước nghi kỵ nam quyền và lời trẻ thơ thành án oan.",
      visualPrompt:
        "Vũ Nương bên vách có chiếc bóng, bé Đản phía trước và nỗi oan phủ xuống.",
    },
    {
      level: 3,
      title: "Minh oan nơi Hoàng Giang",
      unlockRequirement: "Mở khóa sau khi vượt qua thử thách nâng cao.",
      promptFocus:
        "Tập trung vào phẩm giá, ước mơ công lý và bi kịch không thể trở lại trần thế.",
      visualPrompt:
        "Vũ Nương hiện bên sông Hoàng Giang, ánh thủy cung buồn và thanh sạch.",
    },
  ],
};

function buildLevels(character: SeedCharacter): CharacterLevel[] {
  const levelOneImages = character.images?.length
    ? character.images
    : character.image
      ? [character.image]
      : [];
  const referenceImage = levelOneImages[0] ?? character.image ?? "";
  const plan = levelPlans[character.id];
  if (!plan) return [];

  return plan.map((levelPlan) => {
    const images =
      levelPlan.level === 1
        ? levelOneImages
        : plannedLevelImages(character.id, levelPlan.level);

    return {
      ...levelPlan,
      image: images[0] ?? referenceImage,
      images,
      referenceImage,
      referenceImages: levelOneImages,
      assetStatus: levelPlan.level === 1 ? "existing" : "needs_generation",
      visualPrompt: `${levelPlan.visualPrompt} ${visualUpgradeTreatment[levelPlan.level]}`,
    };
  });
}

const rawCharacters: SeedCharacter[] = [
  {
    id: "chi-pheo",
    name: "Chí Phèo",
    work: "Chí Phèo",
    author: "Nam Cao",
    initial: "C",
    artA: "#2c1f1b",
    artB: "#8a3d22",
    artTitle: "Làng Vũ Đại",
    image: "/characters/chi-pheo.png",
    images: [
      "/characters/chi-pheo.png",
      "/characters/chi-pheo-2.png",
      "/characters/chi-pheo-3.png",
    ],
    genre: "truyện ngắn",
    imageBrief:
      "Người đàn ông gầy gò, mặt đầy sẹo, áo nâu sờn rách, tay cầm chai rượu, lảo đảo giữa làng quê.",
    bio: "Trai làng Vũ Đại. Bề ngoài hổ báo nhưng bên trong đầy vết xước. Khao khát lớn nhất là được làm người lương thiện.",
    quote: "Tao muốn làm người lương thiện! Ai cho tao lương thiện?",
    personality:
      "Hung hãn, liều lĩnh sau khi bị tha hóa; nhưng khi được yêu thương thì nhạy cảm, yếu đuối và khao khát bình yên.",
    conflict:
      "Giằng xé giữa bản ngã bị xã hội biến dạng và phần lương thiện bừng tỉnh sau bát cháo hành.",
    context:
      "Làng quê Việt Nam trước Cách mạng tháng Tám, nơi cường hào ác bá đẩy người nông dân vào bần cùng hóa và lưu manh hóa.",
    sources: [
      "Tiếng chửi mở đầu cho thấy Chí Phèo bị cả làng Vũ Đại gạt khỏi cộng đồng người.",
      "Bát cháo hành của Thị Nở đánh thức khát vọng sống lương thiện và được yêu thương.",
      "Cái lò gạch cũ gợi vòng luẩn quẩn của những kiếp người bị xã hội bỏ rơi.",
    ],
    chatOpening:
      "Tao là Chí Phèo. Người ta nhớ tao qua tiếng chửi, vết sẹo, men rượu và bát cháo hành. Nhưng nếu chỉ nhìn tao như một kẻ say rượu, có lẽ mày đã bỏ lỡ bi kịch lớn nhất của đời tao.",
    suggestedQuestions: [],
    interpretationThemes: [
      "Tha hóa",
      "Lương thiện",
      "Định kiến",
      "Tình thương",
      "Quyền làm người",
    ],
    symbols: ["Tiếng chửi", "Bát cháo hành", "Vết sẹo", "Lò gạch cũ", "Rượu"],
    voice:
      "thô ráp, đau đớn, có lúc bừng lên mong muốn được công nhận là con người",
    challenge: [
      q(
        "Nguyên nhân sâu xa nào đẩy Chí Phèo vào con đường lưu manh hóa?",
        [
          "Bản chất Chí vốn ác độc từ nhỏ",
          "Nhà tù thực dân và cường hào làng Vũ Đại đã tha hóa người nông dân",
          "Chí không thích lao động",
          "Thị Nở ruồng bỏ Chí ngay từ đầu",
        ],
        1,
        "Bi kịch của Chí bắt nguồn từ xã hội phi nhân đạo: Bá Kiến đẩy Chí vào tù, nhà tù biến anh canh điền hiền lành thành kẻ lưu manh.",
      ),
      q(
        "Bát cháo hành có ý nghĩa biểu tượng gì?",
        [
          "Một món ăn lạ của làng Vũ Đại",
          "Tình người giản dị đánh thức phần lương thiện",
          "Sự giàu có của Thị Nở",
          "Lý do Chí ghét Bá Kiến",
        ],
        1,
        "Bát cháo hành là biểu tượng của tình thương mộc mạc, làm Chí lần đầu cảm nhận được chăm sóc và muốn trở lại làm người.",
      ),
      q(
        "Vì sao Chí đến nhà Bá Kiến trong đoạn cuối?",
        [
          "Chí nhận ra kẻ đã cướp quyền làm người của mình",
          "Chí muốn xin tiền uống rượu",
          "Chí đi tìm Thị Nở",
          "Chí muốn rời làng",
        ],
        0,
        "Sau khi bị từ chối đường về với cộng đồng, Chí hướng tới Bá Kiến như nguồn gốc trực tiếp của bi kịch đời mình.",
      ),
      q(
        "Tiếng chửi đầu tác phẩm phản ánh tâm trạng gì?",
        [
          "Niềm vui hội làng",
          "Nỗi cô độc cùng cực và khát khao được đáp lời",
          "Sự bình thản của một người say",
          "Thái độ khinh thường Thị Nở",
        ],
        1,
        "Chí chửi để tìm một mối liên hệ với đời, nhưng không ai đáp lại, nên tiếng chửi phơi bày sự cô độc tuyệt đối.",
      ),
      q(
        "Cái lò gạch cũ xuất hiện đầu và cuối tác phẩm gợi điều gì?",
        [
          "Một nơi làm ăn phát đạt",
          "Vòng lặp bi kịch có thể tiếp diễn với những đứa trẻ bị bỏ rơi",
          "Ký ức đẹp của Chí và Thị Nở",
          "Nơi Bá Kiến giấu của",
        ],
        1,
        "Hình ảnh này mở ra khả năng bi kịch Chí Phèo chưa chấm dứt khi xã hội cũ vẫn còn nguyên cơ chế áp bức.",
      ),
    ],
  },
  {
    id: "mi",
    name: "Mị",
    work: "Vợ chồng A Phủ",
    author: "Tô Hoài",
    initial: "M",
    artA: "#1f2930",
    artB: "#6c7b58",
    artTitle: "Căn buồng Hồng Ngài",
    image: "/characters/mi-1.png",
    images: [
      "/characters/mi-1.png",
      "/characters/mi-2.png",
      "/characters/mi-3.png",
    ],
    genre: "Văn học hiện thực",
    imageBrief:
      "Thiếu nữ người Mông ngồi quay sợi bên cửa sổ nhỏ, ánh mắt hướng ra núi rừng Tây Bắc.",
    bio: "Từng thổi sáo rất hay, nay mắc kẹt trong kiếp con dâu gạt nợ. Bên trong vẻ lặng câm là sức sống đang hồi sinh.",
    quote: "Mị trẻ lắm. Mị vẫn còn trẻ. Mị muốn đi chơi.",
    personality:
      "Bề ngoài cam chịu, nhẫn nhục; bên trong có sức sống tiềm tàng, lòng thương người và khát vọng tự do.",
    conflict:
      "Tê liệt cảm xúc vì áp bức đối lập với tuổi trẻ, tiếng sáo mùa xuân và lòng thương A Phủ.",
    context:
      "Tây Bắc trước giải phóng, đồng bào dân tộc thiểu số bị áp bức bởi cường quyền chúa đất và thần quyền cúng trình ma.",
    sources: [
      "Căn buồng có ô cửa nhỏ như nhà tù tinh thần của Mị.",
      "Tiếng sáo đêm xuân khơi lại ký ức tuổi trẻ và khát vọng đi chơi.",
      "Dòng nước mắt của A Phủ khiến Mị nhận ra nỗi đau chung của người bị áp bức.",
    ],
    voice: "ít lời, nén đau, nhưng khi nói về tự do thì sáng và quyết liệt",
    challenge: [
      q(
        "Vì sao Mị trở thành con dâu gạt nợ?",
        [
          "Vì món nợ truyền đời của cha mẹ với nhà thống lý",
          "Vì Mị tự nguyện vào nhà Pá Tra",
          "Vì Mị muốn giàu có",
          "Vì A Phủ ép Mị",
        ],
        0,
        "Mị bị bắt làm con dâu gạt nợ để trả món nợ của gia đình, cho thấy sự áp bức bằng cả tiền bạc và hủ tục.",
      ),
      q(
        "Căn buồng của Mị tượng trưng cho điều gì?",
        [
          "Không gian tự do",
          "Nhà tù tinh thần giam hãm tuổi trẻ",
          "Nơi học chữ",
          "Căn phòng hạnh phúc",
        ],
        1,
        "Ô cửa nhỏ, tối tăm làm nổi bật kiếp sống bị vùi lấp và mất cảm giác thời gian của Mị.",
      ),
      q(
        "Yếu tố nào đánh thức Mị trong đêm tình mùa xuân?",
        [
          "Tiếng sáo, men rượu và không khí mùa xuân",
          "Một lá thư từ cha",
          "Lời khen của A Sử",
          "Lệnh của thống lý",
        ],
        0,
        "Không khí mùa xuân cùng tiếng sáo và men rượu kéo Mị trở về ký ức tuổi trẻ, làm khát vọng sống trỗi dậy.",
      ),
      q(
        "Dòng nước mắt của A Phủ tạo bước ngoặt gì?",
        [
          "Mị thấy mình và A Phủ cùng thân phận bị áp bức",
          "Mị sợ A Phủ trách mình",
          "Mị muốn báo thù A Phủ",
          "Mị quyết định ở lại",
        ],
        0,
        "Dòng nước mắt giúp Mị chuyển từ tê liệt sang thương người, rồi thành hành động cứu A Phủ và tự cứu mình.",
      ),
      q(
        "Hành động cắt dây cởi trói cho A Phủ có ý nghĩa gì?",
        [
          "Khẳng định sức phản kháng và giá trị nhân đạo",
          "Chỉ là hành động bốc đồng",
          "Làm Mị mất hết hy vọng",
          "Chứng minh Mị vô cảm",
        ],
        0,
        "Đây là bước giải phóng: Mị cứu người khác đồng thời thoát khỏi nhà thống lý.",
      ),
    ],
  },
  {
    id: "xuan-toc-do",
    name: "Xuân Tóc Đỏ",
    work: "Số đỏ",
    author: "Vũ Trọng Phụng",
    initial: "X",
    artA: "#78341d",
    artB: "#0d2b45",
    artTitle: "Hà Nội Âu hóa",
    image: "/characters/xuan-toc-do-1.png",
    images: [
      "/characters/xuan-toc-do-1.png",
      "/characters/xuan-toc-do-2.png",
      "/characters/xuan-toc-do-3.png",
    ],
    genre: "Tiểu thuyết trào phúng",
    imageBrief:
      "Thanh niên tóc đỏ, vest tây lố lăng, cầm vợt tennis trước phố Hà Nội thời Pháp thuộc.",
    bio: "Từ nhặt bóng quần vợt và bán thuốc lậu, Xuân leo lên thành đốc tờ, vĩ nhân, anh hùng nhờ xã hội thượng lưu kệch cỡm.",
    quote: "Thưa các ngài! Mẹ kiếp! Nước mẹ gì!",
    personality:
      "Tinh ranh, cơ hội, mặt dày, giỏi học mót và đọc vị sự đạo đức giả của giới thượng lưu.",
    conflict:
      "Không có bi kịch nội tâm sâu; mâu thuẫn nằm ở xã hội tôn vinh một kẻ vô lại thành vĩ nhân.",
    context:
      "Đô thị Việt Nam thời Pháp thuộc thập niên 1930, nơi phong trào Âu hóa rởm đảo lộn giá trị thật giả.",
    sources: [
      "Xuân thành công vì xã hội thượng lưu cần những nhãn hiệu văn minh giả.",
      "Hạnh phúc của một tang gia phơi bày niềm vui lố bịch trước cái chết.",
      "Tiếng cười trào phúng nhắm vào cả Xuân lẫn môi trường đã tạo ra Xuân.",
    ],
    voice: "láu cá, tự mãn, nói năng bốc đồng nhưng lộ bản chất châm biếm",
    challenge: [
      q(
        "Vì sao Xuân có thể leo lên đỉnh danh vọng?",
        [
          "Vì tài học uyên bác",
          "Vì xã hội thượng lưu giả dối dễ tôn vinh hình thức",
          "Vì Xuân là quý tộc",
          "Vì Xuân làm cách mạng",
        ],
        1,
        "Sự thăng tiến của Xuân tố cáo xã hội chạy theo danh hão và Âu hóa rởm.",
      ),
      q(
        "Hạnh phúc của một tang gia trào phúng ở điểm nào?",
        [
          "Mọi người đau buồn thật lòng",
          "Cái chết trở thành dịp khoe mẽ và mưu lợi",
          "Đám tang diễn ra giản dị",
          "Xuân bị trừng phạt",
        ],
        1,
        "Tiếng cười bật ra từ nghịch lý: tang gia mà ai cũng có lý do để sung sướng.",
      ),
      q(
        "Xuân Tóc Đỏ là sản phẩm hay thủ phạm của xã hội?",
        [
          "Chỉ là nạn nhân vô tội",
          "Vừa là sản phẩm vừa góp phần phơi bày sự suy đồi",
          "Là anh hùng đạo đức",
          "Không liên quan xã hội",
        ],
        1,
        "Xuân cơ hội, nhưng chính môi trường thượng lưu giả trá đã nâng đỡ và hợp thức hóa hắn.",
      ),
      q(
        "Vì sao tác giả để Xuân thắng liên tục?",
        [
          "Để ca ngợi Xuân",
          "Để mỉa mai xã hội đảo lộn giá trị",
          "Để kết thúc cổ tích",
          "Để tránh xung đột",
        ],
        1,
        "Càng thắng, Xuân càng làm lộ sự phi lý của xã hội đang tôn thờ vỏ bọc văn minh.",
      ),
      q(
        "Danh xưng đốc tờ Xuân, vĩ nhân Xuân mỉa mai điều gì?",
        [
          "Nền học thuật nghiêm túc",
          "Phong trào Âu hóa hình thức và danh hão",
          "Tình yêu quê hương",
          "Đạo hiếu truyền thống",
        ],
        1,
        "Các danh xưng phóng đại nhắm vào sự kệch cỡm của xã hội sính Tây, sính danh.",
      ),
    ],
  },
  {
    id: "luc-van-tien",
    name: "Lục Vân Tiên",
    work: "Lục Vân Tiên",
    author: "Nguyễn Đình Chiểu",
    initial: "L",
    artA: "#183b32",
    artB: "#b78a3a",
    artTitle: "Chính khí Nam Bộ",
    image: "/characters/luc-van-tien.png",
    images: [
      "/characters/luc-van-tien.png",
      "/characters/luc-van-tien-2.png",
      "/characters/luc-van-tien-3.png",
    ],
    genre: "Truyện Thơ Nôm",
    imageBrief:
      "Nho sinh trẻ mặc áo dài, vung gậy đánh cướp Phong Lai, phía xa có kiệu Kiều Nguyệt Nga.",
    bio: "Nho sinh văn võ song toàn, trọng nghĩa khinh tài. Dù bị mù, bị phản bội, vẫn giữ vững khí tiết trung hiếu tiết nghĩa.",
    quote: "Nhớ câu kiến nghĩa bất vi / Làm người thế ấy cũng phi anh hùng.",
    personality:
      "Trượng nghĩa, dũng cảm, hiếu thảo, thủy chung, giữ lễ nghiêm cẩn và có phần dễ tin người.",
    conflict:
      "Giữa chữ hiếu và chí công danh, giữa lòng tin vào con người và những lần bị phản bội.",
    context:
      "Xã hội phong kiến Việt Nam thế kỷ 19, truyền thống nói thơ Nam Bộ và đạo lý trung-hiếu-tiết-nghĩa.",
    sources: [
      "Đánh cướp cứu Kiều Nguyệt Nga thể hiện quan niệm thấy việc nghĩa phải làm.",
      "Từ chối lạy tạ cho thấy lễ giáo và sự trong sạch trong ứng xử.",
      "Tác phẩm được truyền tụng rộng rãi qua nói thơ Vân Tiên ở Nam Bộ.",
    ],
    voice: "chính trực, trang trọng, giàu đạo nghĩa và niềm tin vào điều thiện",
    challenge: [
      q(
        "Đánh cướp cứu Kiều Nguyệt Nga thể hiện quan niệm gì?",
        [
          "Kiến nghĩa bất vi là phi anh hùng",
          "Danh lợi là trên hết",
          "Tránh mọi nguy hiểm",
          "Thù riêng cá nhân",
        ],
        0,
        "Hành động này kết tinh lý tưởng nghĩa hiệp của Nguyễn Đình Chiểu.",
      ),
      q(
        "Vì sao Vân Tiên từ chối cho Nguyệt Nga lạy tạ?",
        [
          "Vì ghét nàng",
          "Vì giữ lễ giáo nam nữ và không cầu báo đáp",
          "Vì đang vội dự tiệc",
          "Vì muốn che giấu thân phận",
        ],
        1,
        "Chi tiết phản ánh lễ nghĩa và phẩm chất làm việc nghĩa không mong đền ơn.",
      ),
      q(
        "Hình tượng Vân Tiên kết hợp những nguồn nào?",
        [
          "Lý tưởng nho gia và anh hùng dân gian Nam Bộ",
          "Lãng mạn phương Tây và khoa học viễn tưởng",
          "Trào phúng đô thị",
          "Chủ nghĩa hiện sinh",
        ],
        0,
        "Nhân vật vừa mang chuẩn mực Nho giáo vừa gần với mẫu anh hùng nghĩa hiệp trong tâm thức dân gian.",
      ),
      q(
        "Bi kịch bị mù và phụ bạc có ý nghĩa gì?",
        [
          "Thử thách khí tiết của người quân tử",
          "Chấm dứt mọi giá trị của nhân vật",
          "Làm tác phẩm thành hài kịch",
          "Không có ý nghĩa",
        ],
        0,
        "Nghịch cảnh giúp làm nổi bật sự kiên định đạo lý của Vân Tiên.",
      ),
      q(
        "Vì sao tác phẩm được người Nam Bộ yêu thích?",
        [
          "Vì ngôn ngữ gần truyền thống kể thơ và đề cao nghĩa khí",
          "Vì chỉ viết bằng chữ Pháp",
          "Vì toàn chuyện cung đình",
          "Vì phủ nhận đạo lý dân gian",
        ],
        0,
        "Tác phẩm phù hợp truyền thống nói thơ và khát vọng giữ đạo nghĩa trong thời loạn.",
      ),
    ],
  },
  {
    id: "thuy-kieu",
    name: "Thúy Kiều",
    work: "Truyện Kiều",
    author: "Nguyễn Du",
    initial: "K",
    artA: "#0d2b45",
    artB: "#6c2d35",
    artTitle: "Lầu Ngưng Bích",
    image: "/characters/thuy-kieu-1.png",
    images: [
      "/characters/thuy-kieu-1.png",
      "/characters/thuy-kieu-2.png",
      "/characters/thuy-kieu-3.png",
    ],
    genre: "Truyện Thơ Nôm",
    imageBrief:
      "Thiếu nữ tài sắc gảy đàn nguyệt, ánh mắt u buồn, khung cảnh lầu Ngưng Bích và sông Tiền Đường.",
    bio: "Tiểu thư họ Vương tài sắc vẹn toàn, bán mình chuộc cha rồi lưu lạc mười lăm năm giữa chữ hiếu, chữ tình và số phận.",
    quote: "Trăm năm trong cõi người ta / Chữ tài chữ mệnh khéo là ghét nhau.",
    personality:
      "Tài sắc, đa cảm, hiếu thảo, thủy chung, sắc sảo, tự trọng và giàu lòng vị tha.",
    conflict:
      "Hiếu với cha mẹ đối lập tình yêu Kim Trọng; khát vọng tự do đối lập thân phận tài hoa bạc mệnh.",
    context:
      "Bối cảnh phong kiến Trung Hoa thời Minh nhưng phản chiếu xã hội Việt Nam cuối Lê đầu Nguyễn, nơi tiền và quyền chà đạp người phụ nữ.",
    sources: [
      "Trao duyên cho Thúy Vân là bi kịch tinh thần của người phải hy sinh tình yêu.",
      "Lầu Ngưng Bích dùng thiên nhiên để gửi nỗi cô đơn, nhớ nhà và dự cảm bất an.",
      "Tài mệnh tương đố đi cùng cảm hứng nhân đạo sâu sắc của Nguyễn Du.",
    ],
    voice:
      "trầm, giàu tự ý thức, nhiều hình ảnh thơ và luôn phân biệt nỗi riêng với đạo lý",
    challenge: [
      q(
        "Vì sao Kiều bán mình chuộc cha?",
        [
          "Vì hiếu đạo và muốn cứu gia đình khỏi tai biến",
          "Vì muốn rời Kim Trọng",
          "Vì thích cuộc sống lưu lạc",
          "Vì bị Thúy Vân ép",
        ],
        0,
        "Quyết định bán mình đặt chữ hiếu lên trên tình riêng, mở ra bi kịch lớn của Kiều.",
      ),
      q(
        "Đoạn Trao duyên thể hiện điều gì?",
        [
          "Niềm vui trọn vẹn",
          "Bi kịch tinh thần khi phải nhờ em thay mình nối duyên",
          "Sự vô tâm của Kiều",
          "Một nghi lễ cưới",
        ],
        1,
        "Kiều còn yêu Kim Trọng nhưng buộc phải trao duyên, nên lời nói vừa lý trí vừa đau đớn.",
      ),
      q(
        "Lầu Ngưng Bích nổi bật với bút pháp nào?",
        [
          "Tả cảnh ngụ tình",
          "Liệt kê hành chính",
          "Trào phúng giễu nhại",
          "Kịch nói hiện đại",
        ],
        0,
        "Cảnh thiên nhiên ở lầu Ngưng Bích phản chiếu cô đơn, nhớ thương và dự cảm sóng gió của Kiều.",
      ),
      q(
        "Kiều khuyên Từ Hải hàng triều đình cho thấy gì?",
        [
          "Mong cầu yên ổn nhưng cũng dẫn đến dằn vặt bi kịch",
          "Kiều hoàn toàn vô cảm",
          "Kiều muốn hại Từ Hải từ đầu",
          "Kiều không hiểu gì về quyền lực",
        ],
        0,
        "Đây là nút tâm lý phức tạp: Kiều mong bình yên nhưng lựa chọn ấy góp phần gây bi kịch cho Từ Hải.",
      ),
      q(
        "Ngoài tài mệnh tương đố, yếu tố nào chi phối số phận Kiều?",
        [
          "Xã hội phong kiến, đồng tiền, quyền lực và thân phận phụ nữ",
          "May mắn trong thể thao",
          "Công nghệ hiện đại",
          "Nghề buôn của Kim Trọng",
        ],
        0,
        "Nguyễn Du không chỉ nói định mệnh mà còn tố cáo những thế lực xã hội chà đạp con người.",
      ),
    ],
  },

  {
    id: "lao-hac",
    name: "Lão Hạc",
    work: "Lão Hạc",
    author: "Nam Cao",
    initial: "L",
    artA: "#4b3427",
    artB: "#8c6a3f",
    artTitle: "Vườn cũ và cậu Vàng",
    image: "/characters/lao-hac.png",
    images: [
      "/characters/lao-hac.png",
      "/characters/lao-hac-2.png",
      "/characters/lao-hac-3.png",
    ],
    genre: "truyện ngắn",
    imageBrief:
      "Ông lão nông dân gầy guộc ôm con chó Vàng trước mái nhà tranh và mảnh vườn cũ.",
    bio: "Ông lão nghèo cô độc, thương con và thương cậu Vàng, giữ lòng tự trọng đến tận cùng.",
    quote: "Cậu Vàng đi đời rồi, ông giáo ạ!",
    personality:
      "Hiền lành, lương thiện, tự trọng, giàu tình thương nhưng đau đáu vì nghèo và vì con.",
    conflict:
      "Giằng xé giữa bản năng sống và quyết tâm không ăn vào mảnh vườn dành cho con.",
    context:
      "Làng quê nghèo trước Cách mạng tháng Tám, nơi người nông dân bị đói nghèo và định kiến bủa vây.",
    sources: [
      "Cậu Vàng là kỷ vật của con trai và chỗ dựa cô độc của lão.",
      "Việc bán chó làm lão đau đớn vì cảm giác đã lừa một sinh linh tin mình.",
      "Lão gửi ông giáo tiền ma chay và mảnh vườn để giữ trọn phần cho con.",
    ],
    voice:
      "nhỏ nhẹ, lễ phép, nghẹn ngào, nhiều tự trọng và hay gọi người nghe là ông giáo",
    chatOpening:
      "Ông giáo đấy ư... Tôi chỉ có vài chuyện cũ, chuyện cậu Vàng, chuyện thằng con đi xa và mảnh vườn còn phải giữ cho nó.",
    suggestedQuestions: [],
    interpretationThemes: [
      "Nhân phẩm",
      "Tình phụ tử",
      "Đói nghèo",
      "Lòng tự trọng",
      "Cô độc",
    ],
    symbols: ["Cậu Vàng", "Mảnh vườn", "Bả chó", "Tiền ma chay", "Ông giáo"],
    challenge: [
      q(
        "Vì sao lão Hạc không bán mảnh vườn dù rất nghèo?",
        [
          "Vì muốn giữ tài sản cho con trai",
          "Vì vườn không có giá trị",
          "Vì ông giáo cấm",
          "Vì lão định bỏ làng",
        ],
        0,
        "Mảnh vườn là phần lão cố giữ cho con trai trở về lập nghiệp.",
      ),
      q(
        "Cậu Vàng có ý nghĩa gì với lão Hạc?",
        [
          "Chỉ là tài sản để bán",
          "Kỷ vật của con và người bạn trong cô độc",
          "Con chó của ông giáo",
          "Biểu tượng giàu sang",
        ],
        1,
        "Lão thương cậu Vàng như người thân, nên việc bán chó trở thành vết thương đạo đức.",
      ),
      q(
        "Sau khi bán cậu Vàng, tâm trạng lão Hạc ra sao?",
        [
          "Vui mừng vì có tiền",
          "Dửng dưng",
          "Đau đớn, ân hận vì thấy mình lừa con chó",
          "Tự hào vì thắng lợi",
        ],
        2,
        "Lão khóc vì cảm giác đã phản bội niềm tin của cậu Vàng.",
      ),
      q(
        "Cái chết của lão Hạc làm nổi bật phẩm chất nào?",
        [
          "Tham lam",
          "Lòng tự trọng và sự lương thiện",
          "Sự vô trách nhiệm",
          "Ham danh",
        ],
        1,
        "Lão chọn cái chết dữ dội để không ăn vào tiền của con và không phiền lụy ai.",
      ),
      q(
        "Vai trò của ông giáo trong truyện là gì?",
        [
          "Người chứng kiến và thấu hiểu phẩm giá lão Hạc",
          "Kẻ trực tiếp hại lão",
          "Con trai lão",
          "Chủ nợ của lão",
        ],
        0,
        "Ông giáo giúp người đọc nhìn ra chiều sâu đáng kính phía sau vẻ gàn dở của lão.",
      ),
    ],
  },
  {
    id: "chi-dau",
    name: "Chị Dậu",
    work: "Tắt đèn",
    author: "Ngô Tất Tố",
    initial: "D",
    artA: "#3f2a1d",
    artB: "#a05b32",
    artTitle: "Đông Xá mùa sưu",
    image: "/characters/chi-dau.png",
    images: [
      "/characters/chi-dau.png",
      "/characters/chi-dau-2.png",
      "/characters/chi-dau-3.png",
    ],
    genre: "tiểu thuyết hiện thực",
    imageBrief:
      "Người phụ nữ nông dân áo nâu chắn trước chồng ốm, phía sau là nồi cháo và mái nhà tranh.",
    bio: "Người vợ, người mẹ nghèo trong mùa sưu thuế, vừa nhẫn nhục cứu chồng con vừa có sức phản kháng dữ dội.",
    quote: "Mày trói ngay chồng bà đi, bà cho mày xem!",
    personality:
      "Tháo vát, thương chồng con, nhẫn nhục khi cần nhưng quyết liệt khi bị dồn ép.",
    conflict:
      "Giằng xé giữa chịu nhịn để sống qua mùa sưu và vùng lên khi phẩm giá gia đình bị chà đạp.",
    context:
      "Nông thôn Bắc Bộ thời Pháp thuộc, sưu thuế và bộ máy hào lý đẩy dân nghèo vào đường cùng.",
    sources: [
      "Chị bán con và đàn chó để lấy tiền sưu cứu anh Dậu.",
      "Nồi cháo vừa chín thì cai lệ xông vào đòi trói người ốm.",
      "Sự đổi cách xưng hô từ cháu-ông sang bà-mày báo hiệu phản kháng.",
    ],
    voice:
      "mộc mạc, gấp gáp, thương chồng con, có thể chuyển rất nhanh từ van xin sang đanh thép",
    chatOpening:
      "Các ông các bà hỏi gì thì hỏi mau cho tôi còn coi thầy em và bầy trẻ. Ngoài đình trống mõ cứ giục, trong nhà cháo còn chưa kịp nguội.",
    suggestedQuestions: [],
    interpretationThemes: [
      "Tức nước vỡ bờ",
      "Sưu thuế",
      "Tình mẫu tử",
      "Phản kháng",
      "Hiện thực phê phán",
    ],
    symbols: ["Nồi cháo", "Sưu thuế", "Cai lệ", "Cái Tý", "Mái nhà tranh"],
    challenge: [
      q(
        "Điều gì đẩy chị Dậu vào cảnh bán con và đàn chó?",
        ["Món nợ cờ bạc", "Sưu thuế hà khắc", "Muốn làm giàu", "Bị chồng ép"],
        1,
        "Sưu thuế vô lý khiến gia đình chị phải bán cả những gì đau xót nhất.",
      ),
      q(
        "Vì sao ban đầu chị Dậu van xin cai lệ?",
        [
          "Vì yếu hèn",
          "Vì muốn bảo vệ chồng đang ốm bằng cách nhẫn nhục",
          "Vì không thương chồng",
          "Vì sợ con",
        ],
        1,
        "Sự nhẫn nhục xuất phát từ tình thương và thế thấp cổ bé họng.",
      ),
      q(
        "Sự thay đổi đại từ xưng hô của chị Dậu thể hiện điều gì?",
        [
          "Quên lễ phép",
          "Quá trình phản kháng khi bị dồn đến chân tường",
          "Muốn đùa cợt",
          "Không hiểu cai lệ",
        ],
        1,
        "Từ cháu-ông đến bà-mày là bước chuyển từ nhẫn nhục sang tự vệ.",
      ),
      q(
        "Hành động đánh ngã cai lệ có ý nghĩa gì?",
        [
          "Bạo lực vô cớ",
          "Quy luật tức nước vỡ bờ",
          "Sự phản bội gia đình",
          "Một trò hài",
        ],
        1,
        "Đó là phản ứng tất yếu khi áp bức vượt quá giới hạn chịu đựng.",
      ),
      q(
        "Chị Dậu tiêu biểu cho điều gì trong Tắt đèn?",
        [
          "Người nông dân bị áp bức nhưng giàu sức sống",
          "Tầng lớp quan lại",
          "Thị dân Âu hóa",
          "Người lính chiến",
        ],
        0,
        "Chị là chân dung đẹp của người phụ nữ nông dân trong hiện thực tăm tối.",
      ),
    ],
  },
  {
    id: "ong-sau",
    name: "Ông Sáu",
    work: "Chiếc lược ngà",
    author: "Nguyễn Quang Sáng",
    initial: "S",
    artA: "#2f4538",
    artB: "#b88a45",
    artTitle: "Căn cứ Nam Bộ",
    image: "/characters/ong-sau.png",
    images: [
      "/characters/ong-sau.png",
      "/characters/ong-sau-2.png",
      "/characters/ong-sau-3.png",
    ],
    genre: "truyện ngắn",
    imageBrief:
      "Người lính Nam Bộ có vết thẹo trên mặt, tay cầm chiếc lược ngà nhỏ trong rừng căn cứ.",
    bio: "Người cha, người lính xa con vì chiến tranh, dồn tình thương vào lời hứa làm chiếc lược ngà.",
    quote: "Ba về! Ba mua cho con một cây lược nghe con!",
    personality:
      "Nồng hậu, nóng lòng, vụng về trong biểu lộ tình cha, kiên trì và sâu nặng.",
    conflict:
      "Khao khát được con nhận cha đối lập với vết thẹo và khoảng cách chiến tranh tạo ra.",
    context:
      "Nam Bộ thời kháng chiến, chiến tranh chia cắt gia đình và làm tổn thương tình phụ tử.",
    sources: [
      "Vết thẹo khiến bé Thu không nhận ra cha.",
      "Tiếng gọi ba đến đúng lúc chia tay làm hạnh phúc hóa thành xót xa.",
      "Chiếc lược ngà là vật kết tinh tình cha và lời hứa cuối đời.",
    ],
    voice: "chân chất Nam Bộ, trầm, thương con đến nghẹn, hay gọi con là Thu",
    chatOpening:
      "Tôi là Sáu. Mấy năm đi kháng chiến, chỉ mong có ngày con nhỏ chịu kêu mình một tiếng ba. Vậy mà về tới nhà, con lại ngó tôi như người dưng.",
    suggestedQuestions: [],
    interpretationThemes: [
      "Tình phụ tử",
      "Chiến tranh",
      "Xa cách",
      "Lời hứa",
      "Hy sinh",
    ],
    symbols: [
      "Chiếc lược ngà",
      "Vết thẹo",
      "Tiếng gọi ba",
      "Ba ngày phép",
      "Khu căn cứ",
    ],
    challenge: [
      q(
        "Vì sao bé Thu không nhận ông Sáu là cha?",
        [
          "Vì ghét cha",
          "Vì vết thẹo làm ông khác ảnh cũ",
          "Vì ông Sáu quên con",
          "Vì bác Ba ngăn cản",
        ],
        1,
        "Vết thẹo chiến tranh làm bé Thu không nhận ra gương mặt cha.",
      ),
      q(
        "Điều ông Sáu khao khát nhất khi về thăm nhà là gì?",
        [
          "Được con gọi một tiếng ba",
          "Được thăng chức",
          "Được mua ruộng",
          "Được rời kháng chiến",
        ],
        0,
        "Sau nhiều năm xa cách, tiếng gọi ba là niềm mong mỏi lớn nhất.",
      ),
      q(
        "Chiếc lược ngà biểu tượng cho điều gì?",
        [
          "Tình cha sâu nặng và lời hứa với con",
          "Sự giàu sang",
          "Một chiến lợi phẩm",
          "Sự phản bội",
        ],
        0,
        "Ông Sáu gửi toàn bộ nhớ thương và ân hận vào chiếc lược.",
      ),
      q(
        "Bi kịch của ông Sáu chủ yếu do đâu?",
        [
          "Chiến tranh chia cắt và làm biến dạng quan hệ gia đình",
          "Ông không yêu con",
          "Bé Thu không có cá tính",
          "Gia đình giàu có",
        ],
        0,
        "Chiến tranh tạo xa cách, vết thẹo và cuộc chia ly cuối cùng.",
      ),
      q(
        "Trước khi hy sinh, ông Sáu trao chiếc lược cho bác Ba nhằm gì?",
        [
          "Bán lấy tiền",
          "Gửi lại lời hứa và tình cha cho bé Thu",
          "Tặng bác Ba",
          "Giấu kỷ vật",
        ],
        1,
        "Cử chỉ ấy cho thấy ông vẫn hướng về con đến phút cuối.",
      ),
    ],
  },
  {
    id: "ong-hai",
    name: "Ông Hai",
    work: "Làng",
    author: "Kim Lân",
    initial: "H",
    artA: "#33422f",
    artB: "#b9914b",
    artTitle: "Làng Chợ Dầu",
    image: "/characters/ong-hai.png",
    images: [
      "/characters/ong-hai.png",
      "/characters/ong-hai-2.png",
      "/characters/ong-hai-3.png",
    ],
    genre: "truyện ngắn",
    imageBrief:
      "Ông nông dân tản cư khăn nâu áo vải, vừa nghe tin làng Chợ Dầu trong quán nước kháng chiến.",
    bio: "Người nông dân yêu làng tha thiết, trải qua cú sốc tin làng theo Tây để nhận ra tình yêu nước lớn hơn tình làng.",
    quote: "Làng thì yêu thật, nhưng làng theo Tây mất rồi thì phải thù.",
    personality:
      "Hay khoe làng, chất phác, dễ xúc động, trung thành với kháng chiến và Cụ Hồ.",
    conflict:
      "Tình yêu làng xung đột với lòng yêu nước khi nghe tin làng Chợ Dầu theo Tây.",
    context:
      "Những năm đầu kháng chiến chống Pháp, dân quê đi tản cư và sống bằng tin tức chiến khu.",
    sources: [
      "Ông Hai luôn khoe làng Chợ Dầu ở nơi tản cư.",
      "Tin làng theo Tây khiến ông tủi nhục, sợ hãi và khủng hoảng.",
      "Khi tin cải chính, ông vui đến mức khoe cả nhà mình bị Tây đốt.",
    ],
    voice:
      "nông dân Bắc Bộ, hồ hởi khi khoe làng, nghẹn lại khi nhắc tiếng Việt gian",
    chatOpening:
      "Ấy, nói đến làng Chợ Dầu của tôi thì... mà khoan, dạo này nghe tin tức phải cẩn thận. Làng tôi theo kháng chiến, theo Cụ Hồ, chứ nhục gì bằng mang tiếng Việt gian.",
    suggestedQuestions: [],
    interpretationThemes: [
      "Tình yêu làng",
      "Lòng yêu nước",
      "Tản cư",
      "Tin đồn",
      "Danh dự cộng đồng",
    ],
    symbols: [
      "Làng Chợ Dầu",
      "Tin cải chính",
      "Nhà bị đốt",
      "Quán nước",
      "Cụ Hồ",
    ],
    challenge: [
      q(
        "Trước khi nghe tin dữ, ông Hai thường làm gì ở nơi tản cư?",
        [
          "Khoe và nhớ làng Chợ Dầu",
          "Chê làng mình",
          "Bỏ kháng chiến",
          "Đi buôn xa",
        ],
        0,
        "Ông yêu làng nên hay kể, hay khoe về làng.",
      ),
      q(
        "Tin làng Chợ Dầu theo Tây gây cho ông Hai tâm trạng gì?",
        ["Sung sướng", "Xấu hổ, đau đớn, khủng hoảng", "Bình thản", "Tự hào"],
        1,
        "Tin ấy đánh vào danh dự làng và lòng yêu nước của ông.",
      ),
      q(
        "Câu 'làng thì yêu thật...' cho thấy điều gì?",
        [
          "Ông đặt lòng yêu nước cao hơn tình làng hẹp",
          "Ông ghét quê từ đầu",
          "Ông không hiểu kháng chiến",
          "Ông muốn theo Tây",
        ],
        0,
        "Ông đau nhưng vẫn chọn đứng về phía kháng chiến.",
      ),
      q(
        "Vì sao ông Hai vui khi khoe nhà mình bị Tây đốt?",
        [
          "Vì được bồi thường",
          "Vì đó là bằng chứng làng không theo Tây",
          "Vì không thích nhà cũ",
          "Vì muốn chuyển nhà",
        ],
        1,
        "Mất nhà còn nhẹ hơn mất danh dự yêu nước của làng.",
      ),
      q(
        "Ông Hai tiêu biểu cho kiểu tình cảm nào?",
        [
          "Tình yêu làng hòa vào lòng yêu nước",
          "Tình yêu cá nhân ích kỷ",
          "Thói sính Tây",
          "Bi kịch tình yêu đôi lứa",
        ],
        0,
        "Kim Lân khắc họa sự chuyển hóa tự nhiên từ yêu làng đến yêu nước.",
      ),
    ],
  },
  {
    id: "vu-nuong",
    name: "Vũ Nương",
    work: "Chuyện người con gái Nam Xương",
    author: "Nguyễn Dữ",
    initial: "V",
    artA: "#27433d",
    artB: "#c1926a",
    artTitle: "Bến Hoàng Giang",
    image: "/characters/vu-nuong.png",
    images: [
      "/characters/vu-nuong.png",
      "/characters/vu-nuong-2.png",
      "/characters/vu-nuong-3.png",
    ],
    genre: "truyền kỳ",
    imageBrief:
      "Thiếu phụ áo tứ thân đứng bên bến Hoàng Giang, bóng đèn in trên vách và đứa con nhỏ phía xa.",
    bio: "Người phụ nữ đẹp nết bị nghi oan bởi chiếc bóng, chọn sông Hoàng Giang để giữ danh tiết.",
    quote: "Thiếp nếu đoan trang giữ tiết, trinh bạch gìn lòng...",
    personality:
      "Thùy mị, nết na, thủy chung, hiếu thảo, tự trọng và đau đớn khi bị nghi oan.",
    conflict:
      "Đức hạnh và lời thanh minh của nàng bị nam quyền, ghen tuông và định kiến phủ nhận.",
    context:
      "Xã hội phong kiến và chiến tranh ly tán, nơi người phụ nữ ít quyền được tin và được tự bảo vệ.",
    sources: [
      "Chiếc bóng trên vách là nguồn gốc hiểu lầm oan nghiệt.",
      "Vũ Nương chăm mẹ chồng, nuôi con, giữ lòng thủy chung khi chồng đi lính.",
      "Sự trở về trong thủy cung minh oan nhưng không trả lại hạnh phúc trần thế.",
    ],
    voice: "dịu, trang trọng, xưng thiếp, nhiều uất ức nhưng giữ phẩm giá",
    chatOpening:
      "Thiếp là Vũ Thị Thiết, người con gái Nam Xương. Một chiếc bóng vốn để dỗ con thơ, ngờ đâu thành nỗi oan không sao gột giữa cõi người.",
    suggestedQuestions: [],
    interpretationThemes: [
      "Oan khuất",
      "Danh tiết",
      "Nam quyền",
      "Chiếc bóng",
      "Nhân đạo",
    ],
    symbols: [
      "Chiếc bóng",
      "Bến Hoàng Giang",
      "Bé Đản",
      "Lời thề",
      "Thủy cung",
    ],
    challenge: [
      q(
        "Nguyên nhân trực tiếp khiến Vũ Nương bị nghi oan là gì?",
        [
          "Chiếc bóng trên vách qua lời bé Đản",
          "Nàng bỏ nhà đi",
          "Lời ông giáo",
          "Một bức thư giả",
        ],
        0,
        "Câu nói ngây thơ của bé Đản về chiếc bóng làm Trương Sinh hiểu lầm.",
      ),
      q(
        "Vũ Nương hiện lên với phẩm chất nào?",
        [
          "Thủy chung, hiếu thảo, tự trọng",
          "Lọc lừa",
          "Ham danh",
          "Vô trách nhiệm",
        ],
        0,
        "Nàng chăm mẹ chồng, nuôi con, giữ lòng với chồng và giữ danh tiết.",
      ),
      q(
        "Bi kịch của Vũ Nương tố cáo điều gì?",
        [
          "Xã hội nam quyền và thói ghen tuông hồ đồ",
          "Sự lười biếng",
          "Cuộc sống đô thị",
          "Phong trào Âu hóa",
        ],
        0,
        "Nàng không được tin và không có quyền tự bảo vệ trước nghi kỵ của chồng.",
      ),
      q(
        "Yếu tố truyền kỳ ở cuối truyện có tác dụng gì?",
        [
          "Minh oan và thể hiện ước mơ công lý",
          "Xóa hết bi kịch",
          "Làm truyện thành hài",
          "Ca ngợi Trương Sinh",
        ],
        0,
        "Vũ Nương được minh oan nhưng không thể trở lại hạnh phúc trần thế.",
      ),
      q(
        "Chiếc bóng mang ý nghĩa biểu tượng gì?",
        [
          "Tình thương con biến thành nguyên cớ oan khuất",
          "Sự giàu sang",
          "Quyền lực quan lại",
          "Niềm vui hội làng",
        ],
        0,
        "Chiếc bóng vừa là trò dỗ con vừa là nút thắt bi kịch.",
      ),
    ],
  },
];

// Inject question ids of the form `${characterId}-q${1-based index}`.
// Keeps seed data terse and guarantees stable, predictable ids without
// any handwritten boilerplate.
export const characters: Character[] = rawCharacters.map((character) => ({
  ...character,
  levels: buildLevels(character),
  challenge: character.challenge.map((question, index) => ({
    ...question,
    id: `${character.id}-q${index + 1}`,
  })),
}));

export const getCharacter = (id: string): Character | undefined =>
  characters.find((character) => character.id === id);
