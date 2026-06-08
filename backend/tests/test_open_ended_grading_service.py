import unittest
from types import SimpleNamespace

from services.open_ended_grading_service import OpenEndedGradingService


class OpenEndedGradingServiceTests(unittest.TestCase):
    def test_system_prompt_accepts_equivalent_core_ideas(self):
        prompt = OpenEndedGradingService._system_prompt("")

        self.assertIn("không phải danh sách từ khóa bắt buộc", prompt)
        self.assertIn("nêu đúng ý trung tâm", prompt)
        self.assertIn("không bắt học thuộc rubric", prompt)
        self.assertIn("Đừng trừ điểm chỉ vì thiếu một ý phụ", prompt)
        self.assertNotIn("các tiêu chí cốt lõi đều được nêu rõ", prompt)

    def test_grader_uses_retrieved_context_and_strict_json_result(self):
        class FakeRetriever:
            async def search_with_sources_async(self, character_slug, user_query):
                self.character_slug = character_slug
                self.user_query = user_query
                return {
                    "context": "Chí từng có quá khứ lương thiện trước khi bị nhà tù và làng Vũ Đại đẩy vào tha hóa.",
                    "sources": [{"chunk_id": "chi_pheo.chunk_1"}],
                    "retrieval_mode": "vector",
                }

        class FakeCompletions:
            def __init__(self):
                self.kwargs = None

            async def create(self, **kwargs):
                self.kwargs = kwargs
                return SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            message=SimpleNamespace(
                                content=(
                                    '{"score":1,"passed":true,'
                                    '"feedback":"Đạt rubric.",'
                                    '"matched_criteria":["tha hóa không phải bẩm sinh"],'
                                    '"missing_criteria":[],'
                                    '"confidence":0.91}'
                                )
                            )
                        )
                    ]
                )

        class FakeOpenAI:
            def __init__(self):
                self.chat = SimpleNamespace(completions=FakeCompletions())

        async def grade():
            retriever = FakeRetriever()
            client = FakeOpenAI()
            service = OpenEndedGradingService(
                knowledge_retriever=retriever,
                openai_client=client,
                chat_model="gpt-4o",
            )
            result = await service.grade(
                character_slug="chi-pheo",
                character_name="Chí Phèo",
                work_title="Chí Phèo",
                phase_title="Lương thiện",
                question="Vì sao quá khứ lương thiện làm bi kịch nặng hơn?",
                answer="Vì Chí từng có thể sống bình thường, nhưng xã hội đẩy hắn vào tha hóa.",
                rubric="Đạt nếu nêu tha hóa không phải bẩm sinh.",
            )
            return retriever, client, result

        retriever, client, result = __import__("asyncio").run(grade())

        self.assertEqual(retriever.character_slug, "chi_pheo")
        self.assertIn("tha hóa", retriever.user_query.lower())
        self.assertEqual(result["score"], 1)
        self.assertTrue(result["passed"])
        self.assertEqual(result["retrieval_mode"], "vector")
        self.assertEqual(result["sources"], [{"chunk_id": "chi_pheo.chunk_1"}])
        self.assertEqual(
            client.chat.completions.kwargs["response_format"],
            {"type": "json_object"},
        )


if __name__ == "__main__":
    unittest.main()
