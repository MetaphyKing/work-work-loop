import os
import shutil
import subprocess

print("==================================================")
print(" TASK 3: REAL THIN END-TO-END RUN (EAO KERNEL)")
print("==================================================")

root = os.path.abspath("e2e_scratch")
if os.path.exists(root):
    shutil.rmtree(root)
os.makedirs(root, exist_ok=True)
os.environ["WWL_ROOT"] = root

draft_path = os.path.join(root, "draft.md")
publish_path = os.path.join(root, "published_draft.md")

with open(draft_path, "w") as f:
    f.write("# ML-COMPILED-REPORT\n" + ("This is valid content. " * 10))

print("[INIT] Booting EAO SQLite Journal via Harness...")
subprocess.run(["python", "hybrid_gate_harness.py", "--draft", draft_path, "--phase", "8", "--slug", "e2e_live", "--publish", publish_path], check=True)

print("\n[SUCCESS] EAO Live End-to-End run completed safely via hybrid_gate_harness.")
