import unittest
import json
from unittest.mock import patch, MagicMock
from providers import ModelRouter, GroqClient, OpenRouterFreeClient, NvidiaNemotronClient
from tools import search_web_grounding
from agent import strategist_node, researcher_node, synthesizer_node, auditor_node, run_multi_agent_stream

class TestVersatileAIEngine(unittest.TestCase):

    def setUp(self):
        self.sample_state = {
            "task": "Explain the difference between SQL and NoSQL databases",
            "plan": "",
            "search_queries": [],
            "research_data": "",
            "draft": "",
            "feedback": "",
            "is_valid": False,
            "quality_score": 10,
            "loop_count": 0,
            "audit_trail": [],
            "metrics": {}
        }

    def test_providers_initialization(self):
        """Verify model router loads providers from environment"""
        router = ModelRouter()
        providers = router.get_available_providers()
        self.assertIsInstance(providers, list)
        print(f"\n[Test] Loaded active providers: {providers}")

    def test_openrouter_free_model_guardrail(self):
        """Ensure OpenRouter strictly enforces :free models"""
        client = OpenRouterFreeClient(api_key="mock_key")
        for model in client.free_models:
            self.assertTrue(model.endswith(":free"), f"Model {model} must end with :free")

    def test_search_web_grounding_fallback(self):
        """Test DuckDuckGo search tool resilience under sandbox or network blocks"""
        results = search_web_grounding("Quantum Computing", max_results=2)
        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 1)
        self.assertIn("title", results[0])
        self.assertIn("snippet", results[0])
        self.assertIn("url", results[0])

    @patch("agent.router.execute")
    def test_strategist_node(self, mock_execute):
        """Test Strategist generates milestones and search queries"""
        mock_execute.return_value = "### Plan\n1. Overview\n2. Comparison\n\n### Search Queries\n- SQL vs NoSQL performance\n- ACID compliance"
        state = strategist_node(self.sample_state)
        self.assertIn("Plan", state["plan"])
        self.assertGreaterEqual(len(state["search_queries"]), 1)
        self.assertEqual(len(state["audit_trail"]), 1)
        self.assertEqual(state["audit_trail"][0]["agent"], "Strategist")

    @patch("agent.search_web_grounding")
    def test_researcher_node(self, mock_search):
        """Test Grounded Researcher attaches citations to state"""
        mock_search.return_value = [
            {"title": "Database Overview", "snippet": "SQL uses relational tables.", "url": "https://example.com/sql"}
        ]
        self.sample_state["search_queries"] = ["SQL vs NoSQL"]
        state = researcher_node(self.sample_state)
        self.assertIn("Database Overview", state["research_data"])
        self.assertEqual(state["audit_trail"][-1]["agent"], "Researcher")

    @patch("agent.router.execute")
    def test_synthesizer_node(self, mock_execute):
        """Test Synthesizer creates markdown draft"""
        mock_execute.return_value = "# SQL vs NoSQL\nSQL is relational while NoSQL is document-based."
        state = synthesizer_node(self.sample_state)
        self.assertIn("SQL vs NoSQL", state["draft"])
        self.assertEqual(state["audit_trail"][-1]["agent"], "Synthesizer")

    @patch("agent.router.execute")
    def test_auditor_approval(self, mock_execute):
        """Test Auditor approves clean draft without hallucinations"""
        mock_execute.return_value = "VERDICT: APPROVED\nSCORE: 9\nFINDINGS:\n- Factually sound\nACTIONABLE INSTRUCTIONS: None"
        state = auditor_node(self.sample_state)
        self.assertTrue(state["is_valid"])
        self.assertEqual(state["quality_score"], 9)

    @patch("agent.router.execute")
    def test_auditor_rejection_triggers_self_correction(self, mock_execute):
        """Test Auditor flags issues and increments loop count"""
        mock_execute.return_value = "VERDICT: REVISE\nSCORE: 5\nFINDINGS:\n- Missing ACID comparison\nACTIONABLE INSTRUCTIONS: Add ACID details"
        state = auditor_node(self.sample_state)
        self.assertFalse(state["is_valid"])
        self.assertEqual(state["loop_count"], 1)
        self.assertIn("REVISE", state["feedback"])

if __name__ == "__main__":
    unittest.main()

