from __future__ import annotations

import copy
import unittest

from tools.case_study_pipeline.evaluation_questions import (
    generate_deterministic_questions,
    validate_evaluation_questions,
)
from tools.case_study_pipeline.handoff_tests import compute_handoff_test_results


CASE_ID = "benchmark_room"
SCENE_SEMANTICS = {
    "semantic_zones": [
        {
            "zone_id": "lobby",
            "name": "Lobby",
            "purpose": "orientation",
            "object_ids": ["desk"],
        },
        {
            "zone_id": "gallery",
            "name": "Gallery",
            "purpose": "learning about fossils",
            "object_ids": ["skeleton"],
        },
        {
            "zone_id": "library",
            "name": "Library",
            "purpose": "reading",
            "object_ids": ["bookcase"],
        },
    ]
}
AGENT_ROLES = {
    "agents": [
        {
            "id": "entry_agent",
            "display_name": "Entry Guide",
            "expertise": ["visitor orientation"],
            "knowledge_tags": ["lobby"],
            "responsible_zone_ids": ["lobby"],
            "grounded_object_ids": ["desk"],
        },
        {
            "id": "fossil_expert",
            "display_name": "Fossil Expert",
            "expertise": ["dinosaur fossils"],
            "knowledge_tags": ["paleontology"],
            "responsible_zone_ids": ["gallery"],
            "grounded_object_ids": ["skeleton"],
        },
        {
            "id": "reading_guide",
            "display_name": "Reading Guide",
            "expertise": ["children's books"],
            "knowledge_tags": ["reading"],
            "responsible_zone_ids": ["library"],
            "grounded_object_ids": ["bookcase"],
        },
    ]
}
HANDOFF_MATRIX = {
    "handoffs": [
        {
            "source_agent_id": "entry_agent",
            "target_agent_id": "fossil_expert",
            "condition": "The question concerns dinosaur fossils.",
            "reason": "The fossil specialist owns the gallery evidence.",
        },
        {
            "source_agent_id": "entry_agent",
            "target_agent_id": "reading_guide",
            "condition": "The question concerns children's books.",
            "reason": "The reading specialist owns the library evidence.",
        },
    ]
}


def _question_payload(questions: list[dict]) -> dict:
    return {
        "schema": "functionalmlds_evaluation_questions",
        "schema_version": "1.0",
        "case_id": CASE_ID,
        "generation_mode": "deterministic",
        "questions": questions,
    }


class EvaluationBenchmarkHardeningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.generated = generate_deterministic_questions(
            case_id=CASE_ID,
            scene_semantics=SCENE_SEMANTICS,
            agent_roles=AGENT_ROLES,
            handoff_matrix=HANDOFF_MATRIX,
        )

    def _validate(self, payload: dict) -> dict:
        return validate_evaluation_questions(
            payload,
            scene_semantics=SCENE_SEMANTICS,
            agent_roles=AGENT_ROLES,
            handoff_matrix=HANDOFF_MATRIX,
        )

    def test_generation_is_deterministic_valid_and_preserves_legacy_fields(self) -> None:
        repeated = generate_deterministic_questions(
            case_id=CASE_ID,
            scene_semantics=copy.deepcopy(SCENE_SEMANTICS),
            agent_roles=copy.deepcopy(AGENT_ROLES),
            handoff_matrix=copy.deepcopy(HANDOFF_MATRIX),
        )

        self.assertEqual(self.generated, repeated)
        self.assertEqual("valid", self.generated["status"])
        for question in self.generated["questions"]:
            self.assertEqual(question["text"], question["utterance"])
            self.assertIn("expected_handoff", question)
            self.assertIn("expected_agent_id", question)
            self.assertEqual(
                question["expected_handoff"],
                question["expected"]["handoff"],
            )
            self.assertEqual(
                question["expected_agent_id"],
                question["expected"]["agent_id"],
            )

    def test_positive_utterances_do_not_leak_target_identity(self) -> None:
        handoffs = [
            question
            for question in self.generated["questions"]
            if question["kind"] == "handoff_decision"
        ]
        self.assertEqual(2, len(handoffs))
        names = {
            agent["id"]: agent["display_name"]
            for agent in AGENT_ROLES["agents"]
        }
        for question in handoffs:
            target = question["expected_handoff_to"]
            utterance = question["utterance"].casefold()
            self.assertNotIn(target.casefold(), utterance)
            self.assertNotIn(target.replace("_", " ").casefold(), utterance)
            self.assertNotIn(names[target].casefold(), utterance)
            self.assertEqual(target, question["expected"]["handoff_to"])
            self.assertTrue(question["expected"]["rationale"])

    def test_negative_ambiguous_and_unknown_cases_are_explicit(self) -> None:
        kinds = [question["kind"] for question in self.generated["questions"]]
        self.assertEqual(len(AGENT_ROLES["agents"]), kinds.count("handoff_negative"))
        self.assertEqual(1, kinds.count("handoff_ambiguous"))
        self.assertEqual(1, kinds.count("handoff_unknown"))

        ambiguous = next(
            question
            for question in self.generated["questions"]
            if question["kind"] == "handoff_ambiguous"
        )
        self.assertFalse(ambiguous["expected_handoff"])
        self.assertEqual("clarify", ambiguous["expected_resolution"])
        self.assertEqual(2, len(ambiguous["candidate_agent_ids"]))

        unknown = next(
            question
            for question in self.generated["questions"]
            if question["kind"] == "handoff_unknown"
        )
        self.assertFalse(unknown["expected_handoff"])
        self.assertEqual("abstain", unknown["expected_resolution"])

    def test_mutations_are_rejected_without_creating_success_evidence(self) -> None:
        leaking = copy.deepcopy(self.generated["questions"])
        positive = next(
            question for question in leaking if question["kind"] == "handoff_decision"
        )
        positive["text"] += " Please route to Fossil Expert."
        positive["utterance"] = positive["text"]
        report = self._validate(_question_payload(leaking))
        self.assertEqual("invalid", report["status"])
        self.assertTrue(any("leaks" in error for error in report["errors"]))

        ambiguous_mutation = copy.deepcopy(self.generated["questions"])
        ambiguous = next(
            question
            for question in ambiguous_mutation
            if question["kind"] == "handoff_ambiguous"
        )
        ambiguous["candidate_agent_ids"] = ambiguous["candidate_agent_ids"][:1]
        report = self._validate(_question_payload(ambiguous_mutation))
        self.assertEqual("invalid", report["status"])
        self.assertTrue(
            any("at least two unique" in error for error in report["errors"])
        )

    def test_handoff_evaluator_separates_positive_accuracy_from_safety(self) -> None:
        chat_tests = []
        for question in self.generated["questions"]:
            if not question["kind"].startswith("handoff_"):
                continue
            positive = question["kind"] == "handoff_decision"
            target = question["expected_handoff_to"]
            chat_tests.append(
                {
                    "question_id": question["question_id"],
                    "kind": question["kind"],
                    "benchmark_class": question["benchmark_class"],
                    "success": True,
                    "active_agent_id": question["active_agent_id"],
                    "response_active_agent_id": (
                        target if positive else question["active_agent_id"]
                    ),
                    "expected_handoff": question["expected_handoff"],
                    "expected_handoff_to": target,
                    "observed_handoff": positive,
                    "observed_handoff_to": target if positive else None,
                    "say_event_count": 2 if positive else 1,
                    "answer_char_count": 80,
                    "expected_resolution": (
                        question.get("expected_resolution")
                        or question["expected"]["resolution"]
                    ),
                    "candidate_agent_ids": question.get("candidate_agent_ids") or [],
                }
            )

        report = compute_handoff_test_results(
            case_id=CASE_ID,
            chat_results={"chat_tests": chat_tests},
            handoff_matrix=HANDOFF_MATRIX,
        )

        self.assertEqual("valid", report["status"])
        self.assertEqual(1.0, report["metrics"]["positive_handoff_success_rate"])
        self.assertEqual(
            1.0,
            report["metrics"]["handoff_safeguard_routing_success_rate"],
        )
        self.assertFalse(report["metrics"]["semantic_resolution_assessed"])
        self.assertTrue(report["warnings"])

        mutated = copy.deepcopy(chat_tests)
        ambiguous = next(
            test for test in mutated if test["kind"] == "handoff_ambiguous"
        )
        ambiguous["observed_handoff"] = True
        ambiguous["observed_handoff_to"] = ambiguous["candidate_agent_ids"][0]
        ambiguous["response_active_agent_id"] = ambiguous["candidate_agent_ids"][0]
        report = compute_handoff_test_results(
            case_id=CASE_ID,
            chat_results={"chat_tests": mutated},
            handoff_matrix=HANDOFF_MATRIX,
        )
        self.assertEqual("invalid", report["status"])
        self.assertTrue(
            any("unintended handoff" in error for error in report["errors"])
        )


if __name__ == "__main__":
    unittest.main()
