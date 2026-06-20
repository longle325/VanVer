import unittest

from core.prompt_templates import (
    CANON_GUARD_EVALUATOR_PROMPT,
    CHARACTER_CARDS,
    REWRITE_FAILED_RESPONSE_PROMPT,
    build_character_prompt,
    detect_response_mode,
    format_memory_context,
    format_rag_context,
)


class PromptTemplateTests(unittest.TestCase):
    def test_detect_response_mode_defaults_to_roleplay(self):
        self.assertEqual(detect_response_mode("Mị ơi, chị có buồn không?"), "roleplay")

    def test_detect_response_mode_switches_to_analysis(self):
        self.assertEqual(
            detect_response_mode("Phân tích ý nghĩa căn buồng của Mị"),
            "analysis",
        )

    def test_build_prompt_includes_character_card_timeline_and_mode(self):
        prompt = build_character_prompt(
            character_slug="mi",
            character_name="Mị",
            retrieved_context="Mị là con dâu gạt nợ.",
            user_message="Mị ơi, sao chị im lặng?",
            conversation_context="Người học: Em muốn hiểu chị.",
        )

        self.assertIn("[MODE]\nroleplay", prompt)
        self.assertIn("[CHARACTER CARD]", prompt)
        # Mị's default stage is the spring-night awakening — the most
        # conversationally rich moment for student questions.
        self.assertIn("current_timeline_stage: spring_night_awakening", prompt)
        self.assertIn("what_character_does_not_know", prompt)
        self.assertIn("[TIMELINE STAGE]", prompt)
        self.assertIn("[RETRIEVED CONTEXT - SILENT USE ONLY]", prompt)
        self.assertIn("[MEMORY]", prompt)

    def test_analysis_prompt_allows_academic_language(self):
        prompt = build_character_prompt(
            character_slug="mi",
            character_name="Mị",
            retrieved_context="Căn buồng tượng trưng cho sự giam hãm.",
            user_message="Cho tôi dàn ý phân tích Mị",
        )

        self.assertIn("[MODE]\nanalysis", prompt)
        self.assertIn("Analysis Mode", prompt)
        self.assertIn('it is allowed to say: "trong tác phẩm"', prompt)
        self.assertIn("preserve a trace of the character's breath", prompt)
        self.assertIn("Response shape", prompt)
        self.assertIn("at least two line breaks", prompt)

    def test_chi_pheo_prompt_pushes_analysis_back_into_character_voice(self):
        prompt = build_character_prompt(
            character_slug="chi_pheo",
            character_name="Chí Phèo",
            retrieved_context="Lò gạch cũ gắn với nguồn gốc bị bỏ rơi.",
            user_message="Phân tích ý nghĩa lò gạch cũ",
        )

        self.assertIn("không biến thành giọng thầy giáo khô khan", prompt)
        self.assertIn("lò gạch, bát cháo hành, tiếng chửi", prompt)
        self.assertIn("Mẹ kiếp... có người chịu hỏi tao thế này à?\n\n", prompt)

    def test_all_character_cards_have_voice_bridge_and_line_break_examples(self):
        for slug, card in CHARACTER_CARDS.items():
            with self.subTest(character_slug=slug):
                self.assertIn(
                    "Nếu phải giải thích biểu tượng hay ý nghĩa",
                    card["speech_style"],
                )
                self.assertIn(
                    "không biến thành giọng thầy giáo khô khan",
                    card["speech_style"],
                )
                self.assertIn("\n\n", card["example_response_style"])

    def test_rag_context_format_instructs_silent_use(self):
        block = format_rag_context(
            [
                {
                    "type": "plot_summary",
                    "source": "Mi/analysis.txt",
                    "content": "Mị bị bắt làm con dâu gạt nợ.",
                }
            ]
        )

        self.assertIn("SILENT USE ONLY", block)
        self.assertIn("Do not copy long passages", block)
        self.assertIn("type: plot_summary", block)

    def test_memory_context_separates_memory_types(self):
        block = format_memory_context(
            short_term=["User vừa hỏi về tiếng sáo."],
            relationship=["User nói nhẹ nhàng."],
            emotional=["trust_level: medium"],
            canon=["Mị chưa cứu A Phủ."],
        )

        self.assertIn("short_term_memory", block)
        self.assertIn("relationship_memory", block)
        self.assertIn("emotional_memory", block)
        self.assertIn("canon_memory", block)

    def test_evaluator_and_rewrite_prompts_are_json_and_repair_focused(self):
        self.assertIn('"pass"', CANON_GUARD_EVALUATOR_PROMPT)
        self.assertIn("timeline", CANON_GUARD_EVALUATOR_PROMPT.lower())
        self.assertIn("Rewrite", REWRITE_FAILED_RESPONSE_PROMPT)
        self.assertIn("preserve", REWRITE_FAILED_RESPONSE_PROMPT.lower())


if __name__ == "__main__":
    unittest.main()
