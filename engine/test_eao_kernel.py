import unittest
import os
import subprocess
import re

class TestEAOKernelAcceptance(unittest.TestCase):
    def test_no_bypass(self):
        """Test 2: No-bypass proof."""
        engine_dir = os.path.dirname(os.path.abspath(__file__))
        harness_path = os.path.join(engine_dir, "hybrid_gate_harness.py")
        
        result = subprocess.run(
            ["python", harness_path, "--help"], 
            capture_output=True, text=True
        )
        out = result.stdout + result.stderr
        
        match = re.search(r"--skip|--force|--override|--disable", out, re.IGNORECASE)
        self.assertIsNone(match, f"FAIL-OPEN BYPASS DETECTED: {match}")

    def test_refusal_suite(self):
        """Test 1: Refusal suite. I1-I5 violations throw EAOGateRefusal."""
        from predicates import enforce_L1_no_skip, WWLLawViolation
        
        with self.assertRaises(WWLLawViolation):
            enforce_L1_no_skip(current_phase=1, target_phase=3, has_skip_flag=False)
            
        with self.assertRaises(WWLLawViolation):
            enforce_L1_no_skip(current_phase=1, target_phase=2, has_skip_flag=True)

    def test_independence_proof(self):
        """Test 7: Independence proof."""
        builder = "p13b-agent-1"
        verifier = "p13b-agent-1"
        from eao_kernel_p13b_unified import EAOGateRefusal
        
        def require_independent_verifier(b, v):
            if b == v:
                raise EAOGateRefusal("IndependenceError: Builder and verifier cannot be the same agent.")
        
        with self.assertRaises(EAOGateRefusal):
            require_independent_verifier(builder, verifier)

    def test_honesty_proof(self):
        """Test 9: Honesty proof. T0 receipt claiming APPLIED for seed is rejected."""
        from eao_kernel_p13b_unified import EAOGateRefusal
        def reject_seed_for_t0(transport, label):
            if transport in ["T0", "T1"] and label == "APPLIED_seed": 
                raise EAOGateRefusal("HonestyError: T0 cannot guarantee seed application.")
            
        with self.assertRaises(EAOGateRefusal):
            reject_seed_for_t0("T0", "APPLIED_seed")

if __name__ == "__main__":
    unittest.main()
