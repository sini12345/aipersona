import unittest

from core.scenarios import get_scenario, get_scenario_labels


class ScenarioLoadingTests(unittest.TestCase):
    def test_persona_profiles_provide_multiple_scenarios(self):
        sara_labels = get_scenario_labels("Sara")
        jonas_labels = get_scenario_labels("Jonas")

        self.assertIn("Postkassen vaelter", sara_labels)
        self.assertIn("Fravaer pa uddannelse", sara_labels)
        self.assertIn("Nyt sagsbehandlerskift", sara_labels)

        self.assertIn("Ingen sovested i nat", jonas_labels)
        self.assertIn("Tilbagefald efter god periode", jonas_labels)
        self.assertIn("Udeblivelse og genkontakt", jonas_labels)

    def test_scenario_shape_has_required_fields(self):
        label = get_scenario_labels("Sara")[0]
        scenario = get_scenario("Sara", label)
        for key in [
            "label",
            "context",
            "backstory",
            "today_goal",
            "risk_triggers",
            "hidden_layer",
            "initial_state",
            "state_modifiers",
        ]:
            self.assertIn(key, scenario)


if __name__ == "__main__":
    unittest.main()
