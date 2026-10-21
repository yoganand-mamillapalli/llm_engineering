import json
import unittest
from unittest.mock import patch

from langchain_core.exceptions import OutputParserException
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from llm_engineering.structured_outputs.demo import TicketTriage, triage_ticket


class TicketTriageTests(unittest.TestCase):
    valid_response = {
        "category": "billing",
        "priority": "high",
        "summary": "The customer reports a duplicate subscription charge.",
        "suggested_reply": "We can review the duplicate charge with you.",
    }

    def triage_with_response(self, response: str) -> TicketTriage:
        fake_model = RunnableLambda(lambda _prompt: AIMessage(content=response))
        with patch(
            "llm_engineering.structured_outputs.demo.create_model",
            return_value=fake_model,
        ):
            return triage_ticket("I was charged twice for my subscription.")

    def test_parses_valid_ticket_triage(self) -> None:
        result = self.triage_with_response(json.dumps(self.valid_response))

        self.assertEqual(result.category, "billing")
        self.assertEqual(result.priority, "high")
        self.assertIn("duplicate", result.summary)

    def test_rejects_unsupported_category(self) -> None:
        response = {**self.valid_response, "category": "weather"}

        with self.assertRaises(OutputParserException):
            self.triage_with_response(json.dumps(response))

    def test_rejects_unsupported_priority(self) -> None:
        response = {**self.valid_response, "priority": "whenever"}

        with self.assertRaises(OutputParserException):
            self.triage_with_response(json.dumps(response))

    def test_rejects_missing_required_field(self) -> None:
        response = {key: value for key, value in self.valid_response.items() if key != "summary"}

        with self.assertRaises(OutputParserException):
            self.triage_with_response(json.dumps(response))

    def test_rejects_malformed_json(self) -> None:
        with self.assertRaises(OutputParserException):
            self.triage_with_response("not JSON")


if __name__ == "__main__":
    unittest.main()