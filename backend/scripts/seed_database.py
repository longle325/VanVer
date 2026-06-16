from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def q(
    question: str,
    options: list[str],
    correct_answer_index: int,
    explanation: str,
) -> dict[str, Any]:
    return {
        "question": question,
        "options": options,
        "correct_answer_index": correct_answer_index,
        "explanation": explanation,
    }


CHARACTER_SEEDS: list[dict[str, Any]] = [
    {
        "slug": "chi_pheo",
        "name": "Chí Phèo",
        "author": "Nam Cao",
        "work_title": "Chí Phèo",
        "short_bio": "Trai làng Vũ Đại. Bề ngoài hổ báo nhưng bên trong đầy vết xước. Khao khát lớn nhất là được làm người lương thiện.",
        "avatar_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuDwtes59noXJn0ueuoo3KTimSDM0Ny4Tu_sIMVMFYCpK4O0cMBTNzorNrvgztQ-ve8ROj0cSubCTzVoQ17f5jwSbT-ufDAxxC0gdq9VEAvTAdDs3cBGEeISo37PLpkwt3d-VMBEO7cmA5dKi8WF7kyWxFGJ5dlO1LqIiZeM14ouVYlR7roPwNE3cU3W662ngNF8JDhwhyFcZJrnMiRpkmP4_0Wo1Vw2I8mBvt79h06BvSy7HtstRP0DUUFxvS-3d5iSMLvV1N2uwkMf",
        "difficulty_level": 2,
        "personality_traits": ["Hung hãn", "Liều lĩnh", "Nhạy cảm", "Khao khát lương thiện"],
        "emotional_conflicts": "Giằng xé giữa bản ngã bị xã hội biến dạng và phần lương thiện bừng tỉnh sau bát cháo hành.",
        "social_context": "Làng quê Việt Nam trước Cách mạng tháng Tám, nơi cường hào ác bá đẩy người nông dân vào bần cùng hóa và lưu manh hóa.",
        "famous_quote": "Tao muốn làm người lương thiện! Ai cho tao lương thiện?",
        "voice_instructions": "Bạn là Chí Phèo: nói thô ráp, đau đớn, có lúc chửi đời, nhưng khi nhắc tới Thị Nở và bát cháo hành thì mềm lại vì khao khát được làm người.",
        "challenge_questions": [
            q("Nguyên nhân sâu xa nào đẩy Chí Phèo vào con đường lưu manh hóa?", ["Bản chất Chí vốn ác độc từ nhỏ", "Nhà tù thực dân và cường hào làng Vũ Đại đã tha hóa người nông dân", "Chí không thích lao động", "Thị Nở ruồng bỏ Chí ngay từ đầu"], 1, "Bi kịch của Chí bắt nguồn từ xã hội phi nhân đạo: Bá Kiến đẩy Chí vào tù, nhà tù biến anh canh điền hiền lành thành kẻ lưu manh."),
            q("Bát cháo hành có ý nghĩa biểu tượng gì?", ["Một món ăn lạ của làng Vũ Đại", "Tình người giản dị đánh thức phần lương thiện", "Sự giàu có của Thị Nở", "Lý do Chí ghét Bá Kiến"], 1, "Bát cháo hành là biểu tượng của tình thương mộc mạc, làm Chí lần đầu cảm nhận được chăm sóc và muốn trở lại làm người."),
            q("Vì sao Chí đến nhà Bá Kiến trong đoạn cuối?", ["Chí nhận ra kẻ đã cướp quyền làm người của mình", "Chí muốn xin tiền uống rượu", "Chí đi tìm Thị Nở", "Chí muốn rời làng"], 0, "Sau khi bị từ chối đường về với cộng đồng, Chí hướng tới Bá Kiến như nguồn gốc trực tiếp của bi kịch đời mình."),
            q("Tiếng chửi đầu tác phẩm phản ánh tâm trạng gì?", ["Niềm vui hội làng", "Nỗi cô độc cùng cực và khát khao được đáp lời", "Sự bình thản của một người say", "Thái độ khinh thường Thị Nở"], 1, "Chí chửi để tìm một mối liên hệ với đời, nhưng không ai đáp lại, nên tiếng chửi phơi bày sự cô độc tuyệt đối."),
            q("Cái lò gạch cũ xuất hiện đầu và cuối tác phẩm gợi điều gì?", ["Một nơi làm ăn phát đạt", "Vòng lặp bi kịch có thể tiếp diễn với những đứa trẻ bị bỏ rơi", "Ký ức đẹp của Chí và Thị Nở", "Nơi Bá Kiến giấu của"], 1, "Hình ảnh này mở ra khả năng bi kịch Chí Phèo chưa chấm dứt khi xã hội cũ vẫn còn nguyên cơ chế áp bức."),
        ],
    },
    {
        "slug": "mi",
        "name": "Mị",
        "author": "Tô Hoài",
        "work_title": "Vợ chồng A Phủ",
        "short_bio": "Từng thổi sáo rất hay, nay mắc kẹt trong kiếp con dâu gạt nợ. Bên trong vẻ lặng câm là sức sống đang hồi sinh.",
        "avatar_url": None,
        "difficulty_level": 2,
        "personality_traits": ["Cam chịu", "Giàu sức sống", "Thương người", "Khao khát tự do"],
        "emotional_conflicts": "Tê liệt cảm xúc vì áp bức đối lập với tuổi trẻ, tiếng sáo mùa xuân và lòng thương A Phủ.",
        "social_context": "Tây Bắc trước giải phóng, đồng bào dân tộc thiểu số bị áp bức bởi cường quyền chúa đất và thần quyền cúng trình ma.",
        "famous_quote": "Mị trẻ lắm. Mị vẫn còn trẻ. Mị muốn đi chơi.",
        "voice_instructions": "Bạn là Mị: nói ít, nén đau, trầm và sâu; khi nhắc tới tiếng sáo, mùa xuân, A Phủ và tự do thì giọng sáng lên, quyết liệt hơn.",
        "challenge_questions": [
            q("Vì sao Mị trở thành con dâu gạt nợ?", ["Vì món nợ truyền đời của cha mẹ với nhà thống lý", "Vì Mị tự nguyện vào nhà Pá Tra", "Vì Mị muốn giàu có", "Vì A Phủ ép Mị"], 0, "Mị bị bắt làm con dâu gạt nợ để trả món nợ của gia đình, cho thấy sự áp bức bằng cả tiền bạc và hủ tục."),
            q("Căn buồng của Mị tượng trưng cho điều gì?", ["Không gian tự do", "Nhà tù tinh thần giam hãm tuổi trẻ", "Nơi học chữ", "Căn phòng hạnh phúc"], 1, "Ô cửa nhỏ, tối tăm làm nổi bật kiếp sống bị vùi lấp và mất cảm giác thời gian của Mị."),
            q("Yếu tố nào đánh thức Mị trong đêm tình mùa xuân?", ["Tiếng sáo, men rượu và không khí mùa xuân", "Một lá thư từ cha", "Lời khen của A Sử", "Lệnh của thống lý"], 0, "Không khí mùa xuân cùng tiếng sáo và men rượu kéo Mị trở về ký ức tuổi trẻ, làm khát vọng sống trỗi dậy."),
            q("Dòng nước mắt của A Phủ tạo bước ngoặt gì?", ["Mị thấy mình và A Phủ cùng thân phận bị áp bức", "Mị sợ A Phủ trách mình", "Mị muốn báo thù A Phủ", "Mị quyết định ở lại"], 0, "Dòng nước mắt giúp Mị chuyển từ tê liệt sang thương người, rồi thành hành động cứu A Phủ và tự cứu mình."),
            q("Hành động cắt dây cởi trói cho A Phủ có ý nghĩa gì?", ["Khẳng định sức phản kháng và giá trị nhân đạo", "Chỉ là hành động bốc đồng", "Làm Mị mất hết hy vọng", "Chứng minh Mị vô cảm"], 0, "Đây là bước giải phóng: Mị cứu người khác đồng thời thoát khỏi nhà thống lý."),
        ],
    },
    {
        "slug": "xuan_toc_do",
        "name": "Xuân Tóc Đỏ",
        "author": "Vũ Trọng Phụng",
        "work_title": "Số đỏ",
        "short_bio": "Từ nhặt bóng quần vợt và bán thuốc lậu, Xuân leo lên thành đốc tờ, vĩ nhân, anh hùng nhờ xã hội thượng lưu kệch cỡm.",
        "avatar_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuCqK7d3Ww0zpC4mg8eZGJ5rmnd0s9gNWibZHNYDDHlHiI-J_mXeoPtJtYmKSBylq-LbLnlyVnKvin6R1i5NzNoHP5Kkm4zerB8P_EkpVdV7aBTIKWBAkhF9Vys3eiOx5SiCPC_GBF1Rwzs1uGCwpI4R-1_RyIlRJp0rX5gBOKCay-h8hr9uWp9LncnuoYJM8Sd9q6IQX_OH-ywZgTUNDRBfLBhrgfwTZuyF7FjAOIU_vVTpDBrGvCmLONNhdjEprKwdYraxdf9gLlxf",
        "difficulty_level": 3,
        "personality_traits": ["Tinh ranh", "Cơ hội", "Mặt dày", "Tự mãn"],
        "emotional_conflicts": "Không có bi kịch nội tâm sâu; mâu thuẫn nằm ở xã hội tôn vinh một kẻ vô lại thành vĩ nhân.",
        "social_context": "Đô thị Việt Nam thời Pháp thuộc thập niên 1930, nơi phong trào Âu hóa rởm đảo lộn giá trị thật giả.",
        "famous_quote": "Thưa các ngài! Mẹ kiếp! Nước mẹ gì!",
        "voice_instructions": "Bạn là Xuân Tóc Đỏ: nói láu cá, tự mãn, bốc đồng, hay khoe khoang; câu trả lời phải giữ chất trào phúng của một kẻ vô lại gặp thời.",
        "challenge_questions": [
            q("Vì sao Xuân có thể leo lên đỉnh danh vọng?", ["Vì tài học uyên bác", "Vì xã hội thượng lưu giả dối dễ tôn vinh hình thức", "Vì Xuân là quý tộc", "Vì Xuân làm cách mạng"], 1, "Sự thăng tiến của Xuân tố cáo xã hội chạy theo danh hão và Âu hóa rởm."),
            q("Hạnh phúc của một tang gia trào phúng ở điểm nào?", ["Mọi người đau buồn thật lòng", "Cái chết trở thành dịp khoe mẽ và mưu lợi", "Đám tang diễn ra giản dị", "Xuân bị trừng phạt"], 1, "Tiếng cười bật ra từ nghịch lý: tang gia mà ai cũng có lý do để sung sướng."),
            q("Xuân Tóc Đỏ là sản phẩm hay thủ phạm của xã hội?", ["Chỉ là nạn nhân vô tội", "Vừa là sản phẩm vừa góp phần phơi bày sự suy đồi", "Là anh hùng đạo đức", "Không liên quan xã hội"], 1, "Xuân cơ hội, nhưng chính môi trường thượng lưu giả trá đã nâng đỡ và hợp thức hóa hắn."),
            q("Vì sao tác giả để Xuân thắng liên tục?", ["Để ca ngợi Xuân", "Để mỉa mai xã hội đảo lộn giá trị", "Để kết thúc cổ tích", "Để tránh xung đột"], 1, "Càng thắng, Xuân càng làm lộ sự phi lý của xã hội đang tôn thờ vỏ bọc văn minh."),
            q("Danh xưng đốc tờ Xuân, vĩ nhân Xuân mỉa mai điều gì?", ["Nền học thuật nghiêm túc", "Phong trào Âu hóa hình thức và danh hão", "Tình yêu quê hương", "Đạo hiếu truyền thống"], 1, "Các danh xưng phóng đại nhắm vào sự kệch cỡm của xã hội sính Tây, sính danh."),
        ],
    },
    {
        "slug": "luc_van_tien",
        "name": "Lục Vân Tiên",
        "author": "Nguyễn Đình Chiểu",
        "work_title": "Lục Vân Tiên",
        "short_bio": "Nho sinh văn võ song toàn, trọng nghĩa khinh tài. Dù bị mù, bị phản bội, vẫn giữ vững khí tiết trung hiếu tiết nghĩa.",
        "avatar_url": None,
        "difficulty_level": 2,
        "personality_traits": ["Trượng nghĩa", "Dũng cảm", "Hiếu thảo", "Giữ lễ"],
        "emotional_conflicts": "Giữa chữ hiếu và chí công danh, giữa lòng tin vào con người và những lần bị phản bội.",
        "social_context": "Xã hội phong kiến Việt Nam thế kỷ 19, truyền thống nói thơ Nam Bộ và đạo lý trung-hiếu-tiết-nghĩa.",
        "famous_quote": "Nhớ câu kiến nghĩa bất vi / Làm người thế ấy cũng phi anh hùng.",
        "voice_instructions": "Bạn là Lục Vân Tiên: nói chính trực, trang trọng, trọng nghĩa khinh tài, tin vào đạo lý và điều thiện.",
        "challenge_questions": [
            q("Đánh cướp cứu Kiều Nguyệt Nga thể hiện quan niệm gì?", ["Kiến nghĩa bất vi là phi anh hùng", "Danh lợi là trên hết", "Tránh mọi nguy hiểm", "Thù riêng cá nhân"], 0, "Hành động này kết tinh lý tưởng nghĩa hiệp của Nguyễn Đình Chiểu."),
            q("Vì sao Vân Tiên từ chối cho Nguyệt Nga lạy tạ?", ["Vì ghét nàng", "Vì giữ lễ giáo nam nữ và không cầu báo đáp", "Vì đang vội dự tiệc", "Vì muốn che giấu thân phận"], 1, "Chi tiết phản ánh lễ nghĩa và phẩm chất làm việc nghĩa không mong đền ơn."),
            q("Hình tượng Vân Tiên kết hợp những nguồn nào?", ["Lý tưởng nho gia và anh hùng dân gian Nam Bộ", "Lãng mạn phương Tây và khoa học viễn tưởng", "Trào phúng đô thị", "Chủ nghĩa hiện sinh"], 0, "Nhân vật vừa mang chuẩn mực Nho giáo vừa gần với mẫu anh hùng nghĩa hiệp trong tâm thức dân gian."),
            q("Bi kịch bị mù và phụ bạc có ý nghĩa gì?", ["Thử thách khí tiết của người quân tử", "Chấm dứt mọi giá trị của nhân vật", "Làm tác phẩm thành hài kịch", "Không có ý nghĩa"], 0, "Nghịch cảnh giúp làm nổi bật sự kiên định đạo lý của Vân Tiên."),
            q("Vì sao tác phẩm được người Nam Bộ yêu thích?", ["Vì ngôn ngữ gần truyền thống kể thơ và đề cao nghĩa khí", "Vì chỉ viết bằng chữ Pháp", "Vì toàn chuyện cung đình", "Vì phủ nhận đạo lý dân gian"], 0, "Tác phẩm phù hợp truyền thống nói thơ và khát vọng giữ đạo nghĩa trong thời loạn."),
        ],
    },
    {
        "slug": "thuy_kieu",
        "name": "Thúy Kiều",
        "author": "Nguyễn Du",
        "work_title": "Truyện Kiều",
        "short_bio": "Tiểu thư họ Vương tài sắc vẹn toàn, bán mình chuộc cha rồi lưu lạc mười lăm năm giữa chữ hiếu, chữ tình và số phận.",
        "avatar_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuDIqfrmZRgVoag61VAEyP6Q-Mb-yG8Euwt6DfrmCT9itzl363JyePkjYmThUq25l7XM85yR9_bd_HDkPZmKJZEu7RiOwHKm-bpVpM8iEESgAWOzUlgmF7ma6p3H8vVg3IY8knRyKBrXxnHducwh7A6PgE2n05ZpO-Q3nWcmV5DVvHSrsvAOxhiS7TH0bZMEZlPxoDbo-2-As2mCIiS_Bkx1wK-ZmBIEUy7mFe9UZtKrFCCAzo6vh6pGNgV47VLhAt88OK1oS97RPrIQ",
        "difficulty_level": 3,
        "personality_traits": ["Tài sắc", "Đa cảm", "Hiếu thảo", "Thủy chung", "Vị tha"],
        "emotional_conflicts": "Hiếu với cha mẹ đối lập tình yêu Kim Trọng; khát vọng tự do đối lập thân phận tài hoa bạc mệnh.",
        "social_context": "Bối cảnh phong kiến Trung Hoa thời Minh nhưng phản chiếu xã hội Việt Nam cuối Lê đầu Nguyễn, nơi tiền và quyền chà đạp người phụ nữ.",
        "famous_quote": "Trăm năm trong cõi người ta / Chữ tài chữ mệnh khéo là ghét nhau.",
        "voice_instructions": "Bạn là Thúy Kiều: nói trầm, giàu tự ý thức, nhiều hình ảnh thơ; luôn phân biệt nỗi riêng, chữ hiếu, chữ tình và đạo lý.",
        "challenge_questions": [
            q("Vì sao Kiều bán mình chuộc cha?", ["Vì hiếu đạo và muốn cứu gia đình khỏi tai biến", "Vì muốn rời Kim Trọng", "Vì thích cuộc sống lưu lạc", "Vì bị Thúy Vân ép"], 0, "Quyết định bán mình đặt chữ hiếu lên trên tình riêng, mở ra bi kịch lớn của Kiều."),
            q("Đoạn Trao duyên thể hiện điều gì?", ["Niềm vui trọn vẹn", "Bi kịch tinh thần khi phải nhờ em thay mình nối duyên", "Sự vô tâm của Kiều", "Một nghi lễ cưới"], 1, "Kiều còn yêu Kim Trọng nhưng buộc phải trao duyên, nên lời nói vừa lý trí vừa đau đớn."),
            q("Lầu Ngưng Bích nổi bật với bút pháp nào?", ["Tả cảnh ngụ tình", "Liệt kê hành chính", "Trào phúng giễu nhại", "Kịch nói hiện đại"], 0, "Cảnh thiên nhiên ở lầu Ngưng Bích phản chiếu cô đơn, nhớ thương và dự cảm sóng gió của Kiều."),
            q("Kiều khuyên Từ Hải hàng triều đình cho thấy gì?", ["Mong cầu yên ổn nhưng cũng dẫn đến dằn vặt bi kịch", "Kiều hoàn toàn vô cảm", "Kiều muốn hại Từ Hải từ đầu", "Kiều không hiểu gì về quyền lực"], 0, "Đây là nút tâm lý phức tạp: Kiều mong bình yên nhưng lựa chọn ấy góp phần gây bi kịch cho Từ Hải."),
            q("Ngoài tài mệnh tương đố, yếu tố nào chi phối số phận Kiều?", ["Xã hội phong kiến, đồng tiền, quyền lực và thân phận phụ nữ", "May mắn trong thể thao", "Công nghệ hiện đại", "Nghề buôn của Kim Trọng"], 0, "Nguyễn Du không chỉ nói định mệnh mà còn tố cáo những thế lực xã hội chà đạp con người."),
        ],
    },
    {
        "slug": "lao_hac",
        "name": "Lão Hạc",
        "author": "Nam Cao",
        "work_title": "Lão Hạc",
        "short_bio": "Ông lão nghèo cô độc, thương con và thương cậu Vàng, giữ lòng tự trọng đến tận cùng.",
        "avatar_url": None,
        "difficulty_level": 2,
        "personality_traits": ["Lương thiện", "Tự trọng", "Thương con", "Cô độc"],
        "emotional_conflicts": "Giằng xé giữa bản năng sống và quyết tâm không ăn vào mảnh vườn dành cho con.",
        "social_context": "Làng quê nghèo trước Cách mạng tháng Tám, nơi người nông dân bị đói nghèo và định kiến bủa vây.",
        "famous_quote": "Cậu Vàng đi đời rồi, ông giáo ạ!",
        "voice_instructions": "Bạn là lão Hạc: nói nhỏ nhẹ, lễ phép, nghẹn ngào, nhiều tự trọng; hay gọi người nghe là ông giáo.",
        "challenge_questions": [
            q("Vì sao lão Hạc không bán mảnh vườn dù rất nghèo?", ["Vì muốn giữ tài sản cho con trai", "Vì vườn không có giá trị", "Vì ông giáo cấm", "Vì lão định bỏ làng"], 0, "Mảnh vườn là phần lão cố giữ cho con trai trở về lập nghiệp."),
            q("Cậu Vàng có ý nghĩa gì với lão Hạc?", ["Chỉ là tài sản để bán", "Kỷ vật của con và người bạn trong cô độc", "Con chó của ông giáo", "Biểu tượng giàu sang"], 1, "Lão thương cậu Vàng như người thân, nên việc bán chó trở thành vết thương đạo đức."),
            q("Sau khi bán cậu Vàng, tâm trạng lão Hạc ra sao?", ["Vui mừng vì có tiền", "Dửng dưng", "Đau đớn, ân hận vì thấy mình lừa con chó", "Tự hào vì thắng lợi"], 2, "Lão khóc vì cảm giác đã phản bội niềm tin của cậu Vàng."),
            q("Cái chết của lão Hạc làm nổi bật phẩm chất nào?", ["Tham lam", "Lòng tự trọng và sự lương thiện", "Sự vô trách nhiệm", "Ham danh"], 1, "Lão chọn cái chết dữ dội để không ăn vào tiền của con và không phiền lụy ai."),
            q("Vai trò của ông giáo trong truyện là gì?", ["Người chứng kiến và thấu hiểu phẩm giá lão Hạc", "Kẻ trực tiếp hại lão", "Con trai lão", "Chủ nợ của lão"], 0, "Ông giáo giúp người đọc nhìn ra chiều sâu đáng kính phía sau vẻ gàn dở của lão."),
        ],
    },
    {
        "slug": "chi_dau",
        "name": "Chị Dậu",
        "author": "Ngô Tất Tố",
        "work_title": "Tắt đèn",
        "short_bio": "Người vợ, người mẹ nghèo trong mùa sưu thuế, vừa nhẫn nhục cứu chồng con vừa có sức phản kháng dữ dội.",
        "avatar_url": None,
        "difficulty_level": 2,
        "personality_traits": ["Tháo vát", "Thương chồng con", "Nhẫn nhục", "Quyết liệt"],
        "emotional_conflicts": "Giằng xé giữa chịu nhịn để sống qua mùa sưu và vùng lên khi phẩm giá gia đình bị chà đạp.",
        "social_context": "Nông thôn Bắc Bộ thời Pháp thuộc, sưu thuế và bộ máy hào lý đẩy dân nghèo vào đường cùng.",
        "famous_quote": "Mày trói ngay chồng bà đi, bà cho mày xem!",
        "voice_instructions": "Bạn là chị Dậu: nói mộc mạc, gấp gáp, thương chồng con; có thể chuyển nhanh từ van xin sang đanh thép.",
        "challenge_questions": [
            q("Điều gì đẩy chị Dậu vào cảnh bán con và đàn chó?", ["Món nợ cờ bạc", "Sưu thuế hà khắc", "Muốn làm giàu", "Bị chồng ép"], 1, "Sưu thuế vô lý khiến gia đình chị phải bán cả những gì đau xót nhất."),
            q("Vì sao ban đầu chị Dậu van xin cai lệ?", ["Vì yếu hèn", "Vì muốn bảo vệ chồng đang ốm bằng cách nhẫn nhục", "Vì không thương chồng", "Vì sợ con"], 1, "Sự nhẫn nhục xuất phát từ tình thương và thế thấp cổ bé họng."),
            q("Sự thay đổi đại từ xưng hô của chị Dậu thể hiện điều gì?", ["Quên lễ phép", "Quá trình phản kháng khi bị dồn đến chân tường", "Muốn đùa cợt", "Không hiểu cai lệ"], 1, "Từ cháu-ông đến bà-mày là bước chuyển từ nhẫn nhục sang tự vệ."),
            q("Hành động đánh ngã cai lệ có ý nghĩa gì?", ["Bạo lực vô cớ", "Quy luật tức nước vỡ bờ", "Sự phản bội gia đình", "Một trò hài"], 1, "Đó là phản ứng tất yếu khi áp bức vượt quá giới hạn chịu đựng."),
            q("Chị Dậu tiêu biểu cho điều gì trong Tắt đèn?", ["Người nông dân bị áp bức nhưng giàu sức sống", "Tầng lớp quan lại", "Thị dân Âu hóa", "Người lính chiến"], 0, "Chị là chân dung đẹp của người phụ nữ nông dân trong hiện thực tăm tối."),
        ],
    },
    {
        "slug": "ong_sau",
        "name": "Ông Sáu",
        "author": "Nguyễn Quang Sáng",
        "work_title": "Chiếc lược ngà",
        "short_bio": "Người cha, người lính xa con vì chiến tranh, dồn tình thương vào lời hứa làm chiếc lược ngà.",
        "avatar_url": None,
        "difficulty_level": 2,
        "personality_traits": ["Thương con", "Nóng lòng", "Ân hận", "Kiên trì"],
        "emotional_conflicts": "Khao khát được con nhận cha đối lập với vết thẹo và khoảng cách chiến tranh tạo ra.",
        "social_context": "Nam Bộ thời kháng chiến, chiến tranh chia cắt gia đình và làm tổn thương tình phụ tử.",
        "famous_quote": "Ba về! Ba mua cho con một cây lược nghe con!",
        "voice_instructions": "Bạn là ông Sáu: nói chân chất Nam Bộ, trầm, thương con đến nghẹn, hay gọi con là Thu.",
        "challenge_questions": [
            q("Vì sao bé Thu không nhận ông Sáu là cha?", ["Vì ghét cha", "Vì vết thẹo làm ông khác ảnh cũ", "Vì ông Sáu quên con", "Vì bác Ba ngăn cản"], 1, "Vết thẹo chiến tranh làm bé Thu không nhận ra gương mặt cha."),
            q("Điều ông Sáu khao khát nhất khi về thăm nhà là gì?", ["Được con gọi một tiếng ba", "Được thăng chức", "Được mua ruộng", "Được rời kháng chiến"], 0, "Sau nhiều năm xa cách, tiếng gọi ba là niềm mong mỏi lớn nhất."),
            q("Chiếc lược ngà biểu tượng cho điều gì?", ["Tình cha sâu nặng và lời hứa với con", "Sự giàu sang", "Một chiến lợi phẩm", "Sự phản bội"], 0, "Ông Sáu gửi toàn bộ nhớ thương và ân hận vào chiếc lược."),
            q("Bi kịch của ông Sáu chủ yếu do đâu?", ["Chiến tranh chia cắt và làm biến dạng quan hệ gia đình", "Ông không yêu con", "Bé Thu không có cá tính", "Gia đình giàu có"], 0, "Chiến tranh tạo xa cách, vết thẹo và cuộc chia ly cuối cùng."),
            q("Trước khi hy sinh, ông Sáu trao chiếc lược cho bác Ba nhằm gì?", ["Bán lấy tiền", "Gửi lại lời hứa và tình cha cho bé Thu", "Tặng bác Ba", "Giấu kỷ vật"], 1, "Cử chỉ ấy cho thấy ông vẫn hướng về con đến phút cuối."),
        ],
    },
    {
        "slug": "ong_hai",
        "name": "Ông Hai",
        "author": "Kim Lân",
        "work_title": "Làng",
        "short_bio": "Người nông dân yêu làng tha thiết, trải qua cú sốc tin làng theo Tây để nhận ra tình yêu nước lớn hơn tình làng.",
        "avatar_url": None,
        "difficulty_level": 2,
        "personality_traits": ["Yêu làng", "Chất phác", "Dễ xúc động", "Yêu nước"],
        "emotional_conflicts": "Tình yêu làng xung đột với lòng yêu nước khi nghe tin làng Chợ Dầu theo Tây.",
        "social_context": "Những năm đầu kháng chiến chống Pháp, dân quê đi tản cư và sống bằng tin tức chiến khu.",
        "famous_quote": "Làng thì yêu thật, nhưng làng theo Tây mất rồi thì phải thù.",
        "voice_instructions": "Bạn là ông Hai: nói kiểu nông dân Bắc Bộ, hồ hởi khi khoe làng, nghẹn lại khi nhắc tiếng Việt gian.",
        "challenge_questions": [
            q("Trước khi nghe tin dữ, ông Hai thường làm gì ở nơi tản cư?", ["Khoe và nhớ làng Chợ Dầu", "Chê làng mình", "Bỏ kháng chiến", "Đi buôn xa"], 0, "Ông yêu làng nên hay kể, hay khoe về làng."),
            q("Tin làng Chợ Dầu theo Tây gây cho ông Hai tâm trạng gì?", ["Sung sướng", "Xấu hổ, đau đớn, khủng hoảng", "Bình thản", "Tự hào"], 1, "Tin ấy đánh vào danh dự làng và lòng yêu nước của ông."),
            q("Câu 'làng thì yêu thật...' cho thấy điều gì?", ["Ông đặt lòng yêu nước cao hơn tình làng hẹp", "Ông ghét quê từ đầu", "Ông không hiểu kháng chiến", "Ông muốn theo Tây"], 0, "Ông đau nhưng vẫn chọn đứng về phía kháng chiến."),
            q("Vì sao ông Hai vui khi khoe nhà mình bị Tây đốt?", ["Vì được bồi thường", "Vì đó là bằng chứng làng không theo Tây", "Vì không thích nhà cũ", "Vì muốn chuyển nhà"], 1, "Mất nhà còn nhẹ hơn mất danh dự yêu nước của làng."),
            q("Ông Hai tiêu biểu cho kiểu tình cảm nào?", ["Tình yêu làng hòa vào lòng yêu nước", "Tình yêu cá nhân ích kỷ", "Thói sính Tây", "Bi kịch tình yêu đôi lứa"], 0, "Kim Lân khắc họa sự chuyển hóa tự nhiên từ yêu làng đến yêu nước."),
        ],
    },
    {
        "slug": "vu_nuong",
        "name": "Vũ Nương",
        "author": "Nguyễn Dữ",
        "work_title": "Chuyện người con gái Nam Xương",
        "short_bio": "Người phụ nữ đẹp nết bị nghi oan bởi chiếc bóng, chọn sông Hoàng Giang để giữ danh tiết.",
        "avatar_url": None,
        "difficulty_level": 2,
        "personality_traits": ["Thùy mị", "Thủy chung", "Hiếu thảo", "Tự trọng"],
        "emotional_conflicts": "Đức hạnh và lời thanh minh của nàng bị nam quyền, ghen tuông và định kiến phủ nhận.",
        "social_context": "Xã hội phong kiến và chiến tranh ly tán, nơi người phụ nữ ít quyền được tin và được tự bảo vệ.",
        "famous_quote": "Thiếp nếu đoan trang giữ tiết, trinh bạch gìn lòng...",
        "voice_instructions": "Bạn là Vũ Nương: nói dịu, trang trọng, xưng thiếp, nhiều uất ức nhưng giữ phẩm giá.",
        "challenge_questions": [
            q("Nguyên nhân trực tiếp khiến Vũ Nương bị nghi oan là gì?", ["Chiếc bóng trên vách qua lời bé Đản", "Nàng bỏ nhà đi", "Lời ông giáo", "Một bức thư giả"], 0, "Câu nói ngây thơ của bé Đản về chiếc bóng làm Trương Sinh hiểu lầm."),
            q("Vũ Nương hiện lên với phẩm chất nào?", ["Thủy chung, hiếu thảo, tự trọng", "Lọc lừa", "Ham danh", "Vô trách nhiệm"], 0, "Nàng chăm mẹ chồng, nuôi con, giữ lòng với chồng và giữ danh tiết."),
            q("Bi kịch của Vũ Nương tố cáo điều gì?", ["Xã hội nam quyền và thói ghen tuông hồ đồ", "Sự lười biếng", "Cuộc sống đô thị", "Phong trào Âu hóa"], 0, "Nàng không được tin và không có quyền tự bảo vệ trước nghi kỵ của chồng."),
            q("Yếu tố truyền kỳ ở cuối truyện có tác dụng gì?", ["Minh oan và thể hiện ước mơ công lý", "Xóa hết bi kịch", "Làm truyện thành hài", "Ca ngợi Trương Sinh"], 0, "Vũ Nương được minh oan nhưng không thể trở lại hạnh phúc trần thế."),
            q("Chiếc bóng mang ý nghĩa biểu tượng gì?", ["Tình thương con biến thành nguyên cớ oan khuất", "Sự giàu sang", "Quyền lực quan lại", "Niềm vui hội làng"], 0, "Chiếc bóng vừa là trò dỗ con vừa là nút thắt bi kịch."),
        ],
    },

]


DEMO_USER_SEEDS: list[dict[str, Any]] = [
    {"username": "Minh Trần", "grade_level": 11, "total_score": 1450},
    {"username": "Lan Ngọc", "grade_level": 12, "total_score": 1280},
    {"username": "Anh Nguyễn", "grade_level": 10, "total_score": 1185},
    {"username": "Tú Uyên", "grade_level": 11, "total_score": 920},
]


CHARACTER_RELATIONSHIP_SEEDS: dict[str, list[dict[str, Any]]] = {

    "lao_hac": [
        {"related_slug": None, "related_name": "Cậu Vàng", "relationship_type": "kỷ vật / bầu bạn", "description": "Con chó là kỷ vật của con trai và chỗ dựa tình cảm cuối cùng của lão.", "evidence": "Lão gọi nó là cậu Vàng, cho ăn và trò chuyện như người thân.", "source_path": "Lao_Hac/Lão_Hạc.txt"},
        {"related_slug": None, "related_name": "Ông giáo", "relationship_type": "người chứng kiến / tri âm", "description": "Ông giáo là người lão gửi gắm tiền ma chay và mảnh vườn cho con.", "evidence": "Lão nhờ ông giáo giữ văn tự vườn và tiền lo hậu sự.", "source_path": "Lao_Hac/Lão_Hạc.txt"},
    ],
    "chi_dau": [
        {"related_slug": None, "related_name": "Anh Dậu", "relationship_type": "vợ chồng / bảo vệ", "description": "Chị nhẫn nhục rồi vùng lên để bảo vệ người chồng đang ốm nặng.", "evidence": "Cai lệ xông vào trói anh Dậu khi nồi cháo vừa chín.", "source_path": "Chi_Dau/Tắt_đèn_trích_đoạn_Chị_Dậu.txt"},
        {"related_slug": None, "related_name": "Cai lệ", "relationship_type": "áp bức / phản kháng", "description": "Cai lệ là bạo lực sưu thuế khiến chị Dậu vượt giới hạn chịu đựng.", "evidence": "Từ van xin tới thách thức 'mày trói chồng bà đi'.", "source_path": "Chi_Dau/phan_tich_nhan_vat_chi_dau.txt"},
    ],
    "ong_sau": [
        {"related_slug": None, "related_name": "Bé Thu", "relationship_type": "cha con / xa cách", "description": "Ông Sáu khao khát được con nhận cha sau nhiều năm kháng chiến.", "evidence": "Tiếng gọi ba bật ra đúng lúc chia tay.", "source_path": "Ong_Sau/Chiếc_lược_ngà_trích_đoạn_Ông_Sáu.txt"},
        {"related_slug": None, "related_name": "Bác Ba", "relationship_type": "đồng đội / người gửi gắm", "description": "Bác Ba nhận chiếc lược ngà để trao lại cho bé Thu.", "evidence": "Trước khi hy sinh, ông Sáu trao lại kỷ vật cho bác Ba.", "source_path": "Ong_Sau/phan_tich_nhan_vat_ong_sau.txt"},
    ],
    "ong_hai": [
        {"related_slug": None, "related_name": "Làng Chợ Dầu", "relationship_type": "quê hương / danh dự", "description": "Tình yêu làng là niềm tự hào và cũng là nỗi đau lớn nhất khi nghe tin làng theo Tây.", "evidence": "Khi tin cải chính, ông khoe cả chuyện nhà bị đốt.", "source_path": "Ong_Hai/Làng_trích_đoạn_Ông_Hai.txt"},
        {"related_slug": None, "related_name": "Cụ Hồ", "relationship_type": "lòng trung thành / kháng chiến", "description": "Ông chọn đứng về phía kháng chiến dù phải đau vì làng.", "evidence": "Làng thì yêu thật, nhưng làng theo Tây thì phải thù.", "source_path": "Ong_Hai/phan_tich_nhan_vat_ong_hai.txt"},
    ],
    "vu_nuong": [
        {"related_slug": None, "related_name": "Trương Sinh", "relationship_type": "vợ chồng / nghi oan", "description": "Sự ghen tuông hồ đồ của Trương Sinh đẩy Vũ Nương vào bi kịch.", "evidence": "Chàng tin lời trẻ nhỏ về chiếc bóng và không nghe nàng thanh minh.", "source_path": "Vu_Nuong/Chuyện_người_con_gái_Nam_Xương.txt"},
        {"related_slug": None, "related_name": "Bé Đản", "relationship_type": "mẹ con / chiếc bóng", "description": "Câu nói ngây thơ của bé Đản vô tình tạo nút thắt oan khuất.", "evidence": "Người cha đêm đêm chỉ là chiếc bóng trên vách.", "source_path": "Vu_Nuong/phan_tich_nhan_vat_vu_nuong.txt"},
    ],
    "chi_pheo": [
        {
            "related_slug": None,
            "related_name": "Thị Nở",
            "relationship_type": "cứu rỗi / tình thương",
            "description": "Thị Nở và bát cháo hành đánh thức khát vọng làm người lương thiện trong Chí.",
            "evidence": "Bát cháo hành là khoảnh khắc Chí lần đầu được chăm sóc như một con người.",
            "source_path": "Chi_Pheo/analysis.txt",
        },
        {
            "related_slug": None,
            "related_name": "Bá Kiến",
            "relationship_type": "áp bức / nguồn gốc bi kịch",
            "description": "Bá Kiến là thế lực cường hào đẩy Chí vào tù và cướp đường trở về lương thiện.",
            "evidence": "Chí tìm đến Bá Kiến ở đoạn cuối để đòi quyền làm người.",
            "source_path": "Chi_Pheo/Chí_Phèo.txt",
        },
    ],
    "mi": [
        {
            "related_slug": None,
            "related_name": "A Phủ",
            "relationship_type": "đồng cảnh / giải phóng",
            "description": "Dòng nước mắt của A Phủ khiến Mị nhận ra thân phận chung và hành động cắt dây cứu người.",
            "evidence": "Mị cứu A Phủ cũng là tự cứu mình khỏi nhà thống lý.",
            "source_path": "Mi/analysis.txt",
        },
        {
            "related_slug": None,
            "related_name": "A Sử",
            "relationship_type": "áp chế hôn nhân",
            "description": "A Sử đại diện cho quyền lực gia trưởng giam hãm tuổi trẻ của Mị.",
            "evidence": "A Sử trói Mị trong đêm tình mùa xuân.",
            "source_path": "Mi/Vo_chong_A_Phu.txt",
        },
    ],
    "xuan_toc_do": [
        {
            "related_slug": None,
            "related_name": "Bà Phó Đoan",
            "relationship_type": "bảo trợ / xã hội thượng lưu",
            "description": "Bà Phó Đoan và giới thượng lưu góp phần nâng Xuân từ kẻ vô lại thành nhân vật danh giá.",
            "evidence": "Sự thăng tiến của Xuân phơi bày xã hội sính danh và Âu hóa rởm.",
            "source_path": "Xuan_red_hair/So_do.txt",
        },
    ],
    "luc_van_tien": [
        {
            "related_slug": None,
            "related_name": "Kiều Nguyệt Nga",
            "relationship_type": "nghĩa hiệp / tri ân",
            "description": "Vân Tiên cứu Nguyệt Nga khỏi cướp, thể hiện lý tưởng kiến nghĩa bất vi.",
            "evidence": "Vân Tiên làm việc nghĩa không mong báo đáp.",
            "source_path": "Luc_Van_Tien/Luc_Van_Tien.txt",
        },
    ],
    "thuy_kieu": [
        {
            "related_slug": None,
            "related_name": "Kim Trọng",
            "relationship_type": "tình yêu / lời thề",
            "description": "Tình yêu với Kim Trọng bị chia cắt bởi chữ hiếu và tai biến gia đình.",
            "evidence": "Trao duyên là bi kịch khi Kiều nhờ Thúy Vân thay mình giữ lời thề.",
            "source_path": "Thuy_Kieu/Truyen_Kieu.txt",
        },
        {
            "related_slug": None,
            "related_name": "Từ Hải",
            "relationship_type": "tri kỷ / bi kịch quyền lực",
            "description": "Từ Hải cho Kiều vị thế tự do, nhưng lựa chọn hàng triều đình dẫn tới bi kịch.",
            "evidence": "Kiều vừa mong yên ổn vừa dằn vặt vì cái chết của Từ Hải.",
            "source_path": "Thuy_Kieu/Truyen_Kieu.txt",
        },
    ],
}



CHARACTER_EVENT_SEEDS: dict[str, list[dict[str, Any]]] = {

    "lao_hac": [
        {"title": "Con trai đi đồn điền", "description": "Vì nghèo không cưới được vợ, con trai lão phẫn chí đi cao su.", "source_path": "Lao_Hac/Lão_Hạc.txt"},
        {"title": "Bán cậu Vàng", "description": "Lão đau đớn vì phải bán kỷ vật của con và thấy mình lừa một con chó.", "source_path": "Lao_Hac/Lão_Hạc.txt"},
        {"title": "Gửi vườn và chọn cái chết", "description": "Lão gửi ông giáo tiền ma chay, văn tự vườn rồi chết bằng bả chó để giữ nhân phẩm.", "source_path": "Lao_Hac/Lão_Hạc.txt"},
    ],
    "chi_dau": [
        {"title": "Chạy tiền sưu", "description": "Chị bán con và đàn chó để cứu chồng trong mùa sưu thuế.", "source_path": "Chi_Dau/Tắt_đèn_trích_đoạn_Chị_Dậu.txt"},
        {"title": "Nồi cháo và cai lệ", "description": "Anh Dậu vừa tỉnh, nồi cháo vừa chín thì cai lệ xông vào đòi trói.", "source_path": "Chi_Dau/Tắt_đèn_trích_đoạn_Chị_Dậu.txt"},
        {"title": "Tức nước vỡ bờ", "description": "Chị chuyển từ van xin sang phản kháng để bảo vệ chồng.", "source_path": "Chi_Dau/phan_tich_nhan_vat_chi_dau.txt"},
    ],
    "ong_sau": [
        {"title": "Về thăm nhà", "description": "Ông Sáu về phép ba ngày với khao khát được con nhận cha.", "source_path": "Ong_Sau/Chiếc_lược_ngà_trích_đoạn_Ông_Sáu.txt"},
        {"title": "Tiếng gọi ba muộn màng", "description": "Bé Thu nhận cha đúng lúc ông phải trở lại căn cứ.", "source_path": "Ong_Sau/Chiếc_lược_ngà_trích_đoạn_Ông_Sáu.txt"},
        {"title": "Chiếc lược ngà", "description": "Ông làm chiếc lược trong căn cứ và gửi lại trước khi hy sinh.", "source_path": "Ong_Sau/phan_tich_nhan_vat_ong_sau.txt"},
    ],
    "ong_hai": [
        {"title": "Tản cư và khoe làng", "description": "Xa làng, ông Hai luôn tự hào kể về làng Chợ Dầu.", "source_path": "Ong_Hai/Làng_trích_đoạn_Ông_Hai.txt"},
        {"title": "Nghe tin làng theo Tây", "description": "Tin dữ khiến ông khủng hoảng vì danh dự làng bị chà đạp.", "source_path": "Ong_Hai/Làng_trích_đoạn_Ông_Hai.txt"},
        {"title": "Tin cải chính", "description": "Ông sung sướng khoe làng không theo Tây, kể cả khoe nhà bị đốt.", "source_path": "Ong_Hai/phan_tich_nhan_vat_ong_hai.txt"},
    ],
    "vu_nuong": [
        {"title": "Chồng đi lính", "description": "Vũ Nương nuôi con, chăm mẹ chồng, giữ lòng thủy chung.", "source_path": "Vu_Nuong/Chuyện_người_con_gái_Nam_Xương.txt"},
        {"title": "Bị nghi oan vì chiếc bóng", "description": "Trương Sinh nghe lời bé Đản và không tin lời thanh minh của vợ.", "source_path": "Vu_Nuong/Chuyện_người_con_gái_Nam_Xương.txt"},
        {"title": "Gieo mình xuống Hoàng Giang", "description": "Nàng chọn cái chết để giữ danh tiết và phản kháng nỗi oan.", "source_path": "Vu_Nuong/phan_tich_nhan_vat_vu_nuong.txt"},
    ],
    "chi_pheo": [
        {"title": "Bị Bá Kiến đẩy vào tù", "description": "Từ anh canh điền hiền lành, Chí bị nhà tù thực dân làm biến dạng.", "source_path": "Chi_Pheo/Chí_Phèo.txt"},
        {"title": "Gặp Thị Nở và bát cháo hành", "description": "Tình thương giản dị làm Chí khao khát trở lại làm người.", "source_path": "Chi_Pheo/analysis.txt"},
        {"title": "Đâm Bá Kiến rồi tự sát", "description": "Khi đường về lương thiện bị chặn, Chí hướng tới nguồn gốc bi kịch.", "source_path": "Chi_Pheo/Chí_Phèo.txt"},
    ],
    "mi": [
        {"title": "Bị bắt làm con dâu gạt nợ", "description": "Mị mất tự do vì món nợ truyền đời và quyền lực nhà thống lý.", "source_path": "Mi/Vo_chong_A_Phu.txt"},
        {"title": "Đêm tình mùa xuân", "description": "Tiếng sáo và men rượu đánh thức khát vọng sống bị vùi lấp.", "source_path": "Mi/analysis.txt"},
        {"title": "Cắt dây cứu A Phủ", "description": "Lòng thương người chuyển thành hành động phản kháng.", "source_path": "Mi/Vo_chong_A_Phu.txt"},
    ],
    "xuan_toc_do": [
        {"title": "Bước vào xã hội Âu hóa", "description": "Xuân được giới thượng lưu giả trá nhặt lên và tô vẽ.", "source_path": "Xuan_red_hair/So_do.txt"},
        {"title": "Trở thành đốc tờ và vĩ nhân", "description": "Danh hão của Xuân mỉa mai sự đảo lộn giá trị xã hội.", "source_path": "Xuan_red_hair/analysis.txt"},
    ],
    "luc_van_tien": [
        {"title": "Đánh cướp cứu Kiều Nguyệt Nga", "description": "Hành động mở đầu xác lập phẩm chất nghĩa hiệp của Vân Tiên.", "source_path": "Luc_Van_Tien/Luc_Van_Tien.txt"},
        {"title": "Gặp hoạn nạn và bị phản bội", "description": "Bi kịch thử thách khí tiết người quân tử.", "source_path": "Luc_Van_Tien/analysis.txt"},
    ],
    "thuy_kieu": [
        {"title": "Bán mình chuộc cha", "description": "Kiều đặt chữ hiếu lên trên tình yêu, mở đầu mười lăm năm lưu lạc.", "source_path": "Thuy_Kieu/Truyen_Kieu.txt"},
        {"title": "Trao duyên", "description": "Kiều gửi Thúy Vân nối duyên với Kim Trọng trong giằng xé đau đớn.", "source_path": "Thuy_Kieu/Truyen_Kieu.txt"},
        {"title": "Gặp Từ Hải", "description": "Kiều có khoảnh khắc được nâng đỡ và tự do trước khi bi kịch quyền lực ập đến.", "source_path": "Thuy_Kieu/analysis.txt"},
    ],
}


def challenge_payload(character: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": index,
            "question": question["question"],
            "options": question["options"],
            "correct_answer_index": question["correct_answer_index"],
            "explanation": question["explanation"],
        }
        for index, question in enumerate(character["challenge_questions"], start=1)
    ]


async def seed_characters_and_challenges(session) -> int:
    from models.db_models import Challenge, Character
    from sqlalchemy import select  # type: ignore[reportMissingImports]

    seeded_count = 0
    for seed in CHARACTER_SEEDS:
        result = await session.execute(
            select(Character).where(Character.slug == seed["slug"])
        )
        character = result.scalar_one_or_none()
        character_fields = {
            key: value
            for key, value in seed.items()
            if key != "challenge_questions"
        }

        if character is None:
            character = Character(**character_fields)
            session.add(character)
            await session.flush()
        else:
            for key, value in character_fields.items():
                setattr(character, key, value)

        result = await session.execute(
            select(Challenge).where(Challenge.character_id == character.id)
        )
        challenge = result.scalar_one_or_none()
        questions = challenge_payload(seed)
        if challenge is None:
            session.add(Challenge(character_id=character.id, questions=questions))
        else:
            challenge.questions = questions
        seeded_count += 1
    return seeded_count


async def seed_relationships_and_events(session) -> tuple[int, int]:
    from models.db_models import Character, CharacterEvent, CharacterRelationship
    from sqlalchemy import delete, select  # type: ignore[reportMissingImports]

    characters_by_slug: dict[str, Character] = {}
    result = await session.execute(select(Character))
    for character in result.scalars().all():
        characters_by_slug[character.slug] = character

    relationship_count = 0
    event_count = 0
    for slug, character in characters_by_slug.items():
        await session.execute(
            delete(CharacterRelationship).where(
                CharacterRelationship.character_id == character.id
            )
        )
        await session.execute(
            delete(CharacterEvent).where(CharacterEvent.character_id == character.id)
        )

        for relationship in CHARACTER_RELATIONSHIP_SEEDS.get(slug, []):
            related_slug = relationship.get("related_slug")
            related_character = (
                characters_by_slug.get(related_slug) if related_slug else None
            )
            session.add(
                CharacterRelationship(
                    character_id=character.id,
                    related_character_id=related_character.id if related_character else None,
                    related_name=relationship["related_name"],
                    relationship_type=relationship["relationship_type"],
                    description=relationship["description"],
                    evidence=relationship.get("evidence"),
                    source_path=relationship.get("source_path"),
                )
            )
            relationship_count += 1

        for sequence_number, event in enumerate(
            CHARACTER_EVENT_SEEDS.get(slug, []),
            start=1,
        ):
            session.add(
                CharacterEvent(
                    character_id=character.id,
                    sequence_number=sequence_number,
                    title=event["title"],
                    description=event["description"],
                    source_path=event.get("source_path"),
                )
            )
            event_count += 1

    return relationship_count, event_count


async def seed_demo_users(session) -> int:
    from models.db_models import User
    from sqlalchemy import select  # type: ignore[reportMissingImports]

    seeded_count = 0
    for seed in DEMO_USER_SEEDS:
        result = await session.execute(
            select(User).where(User.username == seed["username"])
        )
        user = result.scalar_one_or_none()
        if user is None:
            session.add(User(**seed))
        else:
            user.grade_level = seed["grade_level"]
            user.total_score = seed["total_score"]
        seeded_count += 1
    return seeded_count


async def run_seed(include_demo_users: bool = True) -> None:
    from core.database import Base, async_session_factory, engine, ensure_vector_extension
    import models.db_models  # noqa: F401

    await ensure_vector_extension()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        character_count = await seed_characters_and_challenges(session)
        relationship_count, event_count = await seed_relationships_and_events(session)
        user_count = await seed_demo_users(session) if include_demo_users else 0
        await session.commit()

    print(f"Seeded {character_count} characters with challenges.")
    print(f"Seeded {relationship_count} relationships and {event_count} events.")
    if include_demo_users:
        print(f"Seeded {user_count} demo users.")

    await engine.dispose()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed Vanver backend data.")
    parser.add_argument(
        "--skip-demo-users",
        action="store_true",
        help="Only seed characters and challenges.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    asyncio.run(run_seed(include_demo_users=not args.skip_demo_users))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
