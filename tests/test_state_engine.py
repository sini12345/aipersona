import unittest

from core.state_engine import PersonaState, update_state_from_turn


class StateEngineTests(unittest.TestCase):
    def test_validation_increases_trust_and_reduces_stress(self):
        state = PersonaState(trust=35, stress=60, shame=50, hope=40, control_loss=60, difficulty=2)
        updated = update_state_from_turn(
            state,
            "Jeg forstår dig, det giver mening. Hvad tænker du vi kan gøre?",
            "Tak fordi du spørger. Jeg ved ikke helt endnu, men måske kan vi tage ét skridt ad gangen.",
            "Alliance",
        )
        self.assertGreater(updated.trust, state.trust)
        self.assertLess(updated.stress, state.stress)

    def test_pressure_increases_stress_and_control_loss(self):
        state = PersonaState(trust=35, stress=60, shame=50, hope=40, control_loss=60, difficulty=2)
        updated = update_state_from_turn(
            state,
            "Du skal gøre det nu, ellers bliver der konsekvens.",
            "Okay...",
            "Alliance",
        )
        self.assertGreater(updated.stress, state.stress)
        self.assertGreater(updated.control_loss, state.control_loss)
        self.assertLess(updated.trust, state.trust)

    def test_deeskalering_rewards_calm_more_than_alliance(self):
        state = PersonaState(trust=35, stress=60, shame=50, hope=40, control_loss=60, difficulty=2)
        text = "Vi tager det roligt og en ting ad gangen. Hvad tænker du?"
        ai = "Det hjælper faktisk lidt at tage det langsomt."
        updated_alliance = update_state_from_turn(state, text, ai, "Alliance")
        updated_deesk = update_state_from_turn(state, text, ai, "Deeskalering")
        self.assertLess(updated_deesk.stress, updated_alliance.stress)

    def test_difficulty_adds_baseline_resistance(self):
        base = PersonaState(trust=35, stress=60, shame=50, hope=40, control_loss=60, difficulty=2)
        hard = PersonaState(trust=35, stress=60, shame=50, hope=40, control_loss=60, difficulty=3)
        text = "Hej, hvad tænker du?"
        ai = "Jeg ved det ikke."
        updated_base = update_state_from_turn(base, text, ai, "Alliance")
        updated_hard = update_state_from_turn(hard, text, ai, "Alliance")
        self.assertGreaterEqual(updated_hard.stress, updated_base.stress)
        self.assertGreaterEqual(updated_hard.control_loss, updated_base.control_loss)

    def test_caps_prevent_extreme_single_turn_swings(self):
        state = PersonaState(trust=50, stress=50, shame=50, hope=50, control_loss=50, difficulty=2)
        text = " ".join(
            [
                "du skal",
                "du skal bare",
                "ellers",
                "hvis ikke",
                "sanktion",
                "konsekvens",
                "burde",
                "nu gør du",
            ]
        )
        updated = update_state_from_turn(state, text, "Nej.", "Alliance")
        self.assertGreaterEqual(updated.trust, 44)  # cap: max -6
        self.assertLessEqual(updated.stress, 58)  # cap: max +8

    def test_clamp_bounds_0_100(self):
        high = PersonaState(trust=99, stress=99, shame=99, hope=99, control_loss=99, difficulty=3)
        updated_high = update_state_from_turn(
            high,
            "Du skal nu gøre det ellers konsekvens sanktion.",
            "Nej",
            "Alliance",
        )
        low = PersonaState(trust=1, stress=1, shame=1, hope=1, control_loss=1, difficulty=1)
        updated_low = update_state_from_turn(
            low,
            "Jeg forstår dig, det giver mening. Hvad tænker du?",
            "Tak, det hjælper lidt og jeg kan sige mere nu.",
            "Alliance",
        )
        for value in updated_high.to_dict().values():
            self.assertLessEqual(value, 100)
        for value in updated_low.to_dict().values():
            self.assertGreaterEqual(value, 0)

    def test_scenario_modifier_amplifies_pressure_penalty(self):
        state = PersonaState(trust=35, stress=60, shame=50, hope=40, control_loss=60, difficulty=2)
        text = "Du skal gøre det nu ellers bliver der konsekvens."
        ai = "Okay."

        base = update_state_from_turn(state, text, ai, "Alliance")
        modified = update_state_from_turn(
            state,
            text,
            ai,
            "Alliance",
            scenario_modifiers={"pressure_penalty_mult": 1.5},
        )

        self.assertLessEqual(modified.trust, base.trust)
        self.assertGreaterEqual(modified.stress, base.stress)
        self.assertGreaterEqual(modified.control_loss, base.control_loss)


if __name__ == "__main__":
    unittest.main()
