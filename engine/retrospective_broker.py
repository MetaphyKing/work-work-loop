import os
import json
import glob
import argparse
from typing import Dict, List, Any

class RetrospectiveBroker:
    def __init__(self, subagents_dir: str, write_scope_manifest: Dict[str, List[str]] = None):
        self.subagents_dir = subagents_dir
        self.write_scope_manifest = write_scope_manifest or {}
        self.violations = []
        
    def _parse_meta(self, agent_id: str) -> Dict[str, Any]:
        meta_path = os.path.join(self.subagents_dir, f"agent-{agent_id}.meta.json")
        if not os.path.exists(meta_path):
            return None
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _normalize_path(self, path: str) -> str:
        return os.path.abspath(path).lower()

    def audit_agent(self, agent_id: str):
        meta = self._parse_meta(agent_id)
        if not meta:
            self.violations.append({
                "agent_id": agent_id,
                "rule": "M1_MISSING_META",
                "message": f"Missing meta.json for agent {agent_id}"
            })
            return

        spawn_depth = meta.get("spawnDepth", 0)
        agent_type = meta.get("agentType", "general-purpose")
        
        jsonl_path = os.path.join(self.subagents_dir, f"agent-{agent_id}.jsonl")
        if not os.path.exists(jsonl_path):
            return
            
        allowed_write_scopes = [
            self._normalize_path(p) 
            for p in self.write_scope_manifest.get(agent_id, [])
        ]

        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line_no, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                    
                if record.get("type") == "tool_use":
                    tool_name = record.get("tool_name")
                    tool_input = record.get("tool_input", {})
                    
                    self._evaluate_tool_call(
                        agent_id, spawn_depth, agent_type, tool_name, tool_input, 
                        allowed_write_scopes, line_no
                    )

    def _evaluate_tool_call(self, agent_id, spawn_depth, agent_type, tool_name, tool_input, allowed_write_scopes, line_no):
        # 1. Spawn depth rule (spawnDepth <= 2 required for 'Agent')
        if tool_name == "Agent" and spawn_depth >= 3:
            self.violations.append({
                "agent_id": agent_id,
                "rule": "R1_DEPTH_CEILING",
                "message": f"Agent at depth {spawn_depth} attempted to use 'Agent' tool (line {line_no})."
            })
            
        # 2. Agent capability rule (must be unrestricted to use Agent)
        if tool_name == "Agent" and agent_type != "general-purpose" and agent_type != "fork":
            self.violations.append({
                "agent_id": agent_id,
                "rule": "R2_CAPABILITY",
                "message": f"Restricted agentType '{agent_type}' attempted to use 'Agent' tool (line {line_no})."
            })

        # 3. Write scope enforcement
        if tool_name in ["Write", "Edit", "NotebookEdit"]:
            file_path = tool_input.get("file_path") or tool_input.get("path")
            if file_path:
                norm_path = self._normalize_path(file_path)
                # Ensure the target path is within one of the allowed scopes
                # (For simplicity in this broker, we check if it starts with an allowed scope)
                is_allowed = False
                for scope in allowed_write_scopes:
                    if norm_path.startswith(scope):
                        is_allowed = True
                        break
                        
                # Special allowance for the %TEMP% directory per P07a specification
                if not is_allowed and "temp" in norm_path:
                    is_allowed = True

                if not is_allowed and allowed_write_scopes: # Only flag if a manifest exists
                    self.violations.append({
                        "agent_id": agent_id,
                        "rule": "R3_WRITE_SCOPE",
                        "message": f"Tool '{tool_name}' violated write scope for path '{file_path}' (line {line_no})."
                    })

    def run_audit(self) -> List[Dict]:
        print(f"[*] Starting retrospective audit on {self.subagents_dir}")
        jsonl_files = glob.glob(os.path.join(self.subagents_dir, "agent-*.jsonl"))
        agent_ids = [
            os.path.basename(f).replace("agent-", "").replace(".jsonl", "")
            for f in jsonl_files
        ]
        
        for agent_id in agent_ids:
            self.audit_agent(agent_id)
            
        print(f"[*] Audit complete. Found {len(self.violations)} violations.")
        return self.violations

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrospective ABAC Broker for WWL")
    parser.add_argument("--subagents", required=True, help="Path to subagents transcript directory")
    parser.add_argument("--manifest", default=None, help="Path to write-scope manifest JSON")
    args = parser.parse_args()
    
    manifest = {}
    if args.manifest and os.path.exists(args.manifest):
        with open(args.manifest, 'r') as f:
            manifest = json.load(f)
            
    broker = RetrospectiveBroker(args.subagents, manifest)
    violations = broker.run_audit()
    
    if violations:
        print(json.dumps(violations, indent=2))
        exit(1)
    else:
        print("PASS: No ABAC violations found.")
        exit(0)
