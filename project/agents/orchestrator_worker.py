"""
Orchestrator-Worker Pattern for Task Distribution

This module implements the orchestrator-worker pattern where an orchestrator
breaks down work into tasks that are executed by generic workers.
"""

import json
from typing import Dict, List, Any

from openai import OpenAI

from config import Config


def _fallback_orchestration_plan(messages: List[Dict]) -> Dict:
    """Deterministic tasks when orchestrator LLM is unavailable."""
    ids = [
        str(m.get("message_id"))
        for m in messages
        if isinstance(m, dict) and m.get("message_id")
    ]
    return {
        "analysis": "Deterministic fallback plan (API error or invalid JSON).",
        "grouping_plan": {
            "group_by": "message_type",
            "rationale": "Grouped by message category for templated reporting.",
            "groups_preview": [],
        },
        "task_count": 2,
        "tasks": [
            {
                "task_id": "fb_pattern_01",
                "type": "pattern_detection",
                "description": "Flag structural anomalies referencing batch context.",
                "priority": "high",
                "data": {"message_ids": ids, "context": {"mode": "fallback"}},
            },
            {
                "task_id": "fb_summary_01",
                "type": "summary_report",
                "description": (
                    "Emit concise batch summary aligned with grouping_plan dimension."
                ),
                "priority": "medium",
                "data": {"message_ids": ids, "context": {"mode": "fallback"}},
            },
        ],
    }


class OrchestratorWorkerPattern:
    """
    Implements the orchestrator-worker pattern for SWIFT message processing.
    The orchestrator analyzes messages and creates tasks for generic workers.
    """

    def __init__(self) -> None:
        self.config = Config()
        self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)
        self.model = getattr(self.config, "OPENAI_MODEL", "gpt-4o")

    # --- readable, compact CLI logging (mirrors prompt_chaining style) ---

    @staticmethod
    def _compact(text: Any, limit: int = 200) -> str:
        s = str(text).replace("\n", " ").strip()
        return (s[: limit - 3] + "...") if len(s) > limit else s

    @staticmethod
    def _log_phase(label: str, detail: str) -> None:
        print(f"       [{label}] {detail}")

    class Orchestrator:
        """Orchestrator: LLM proposes grouping plan + worker task list."""

        def __init__(self, client: OpenAI, model: str):
            self.client = client
            self.model = model

        def analyze_and_create_tasks(self, messages: List[Dict]) -> Dict:
            system_prompt = """You orchestrate SWIFT MT batch processing.

1) Inspect all messages for risk/complexity.
2) Decide how downstream REPORTS should be GROUPED (e.g. currency, sender_bic,
   message_type) and briefly justify.
3) Emit up to five concrete TASKS workers will execute. Each task MUST include:
   task_id, type, description, priority, data.message_ids (subset of batch IDs).

Allowed task.type values:
compliance_check, fraud_analysis, amount_verification, pattern_detection,
summary_report

Return STRICT JSON."""

            user_prompt = f"""BATCH_JSON:
{json.dumps(messages, indent=2, default=str)}

Return JSON shape:
{{
  "analysis": "executive synopsis",
  "grouping_plan": {{
    "group_by": "<dimension>",
    "rationale": "why grouping helps reporting/compliance here",
    "groups_preview": [{{"group_key": "...", "message_ids": ["..."] }}]
  }},
  "task_count": <number>,
  "tasks": [...]
}}
If batch is tiny, emit 2-3 complementary tasks."""

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.15,
                )
                parsed = json.loads(response.choices[0].message.content or "{}")
            except Exception as e:
                print(f"Orchestrator LLM error: {e}")
                parsed = {}

            if not isinstance(parsed.get("tasks"), list) or not parsed["tasks"]:
                parsed = _fallback_orchestration_plan(messages)
            return parsed

    class GenericAgent:
        """Worker: executes a single orchestrator task via structured LLM output."""

        def __init__(self, client: OpenAI, model: str):
            self.client = client
            self.model = model

        def execute_task(self, task: Dict) -> Dict:
            task_type = task.get("type", "unknown")
            description = task.get("description", "")
            task_data = task.get("data", {})

            role_map = {
                "compliance_check": (
                    "You are a Compliance Specialist executing a narrowly scoped SWIFT "
                    "compliance ticket."
                ),
                "fraud_analysis": (
                    "You are a Fraud Analyst producing evidence-backed findings JSON."
                ),
                "amount_verification": (
                    "You are a Financial Auditor validating amounts/currencies/format."
                ),
                "pattern_detection": (
                    "You are a Pattern Analyst surfacing anomalies and clusters."
                ),
                "summary_report": (
                    "You synthesize managerial reporting consistent with grouping hints."
                ),
            }
            system_prompt = role_map.get(
                task_type,
                "You are a Generic SWIFT Worker. Complete this ticket rigorously.",
            )

            user_prompt = f"""TASK_ID: {task.get('task_id')}
TYPE: {task_type}
DESCRIPTION: {description}

PAYLOAD:
{json.dumps(task_data, indent=2, default=str)}

Respond JSON ONLY:
{{
  "task_id": "{task.get('task_id')}",
  "status": "completed"|"failed",
  "headline": "≤120 chars takeaway",
  "findings": ["bullet strings"],
  "report": {{
     "markdown_summary": "...",
     "metrics": {{ "optional": "kpi map" }},
     "group_alignment": "how output respects orchestrator grouping if applicable"
  }}
}}"""

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.12,
                )
                out = json.loads(response.choices[0].message.content or "{}")
                out.setdefault("task_id", task.get("task_id"))
                out.setdefault("status", "completed")
                return out
            except Exception as e:
                return {
                    "task_id": task.get("task_id"),
                    "status": "failed",
                    "error": str(e),
                    "headline": "LLM failure",
                    "findings": [],
                    "report": {},
                }

    @staticmethod
    def _inject_message_subset(task: Dict, all_messages: List[Dict]) -> Dict:
        """Attach actual message dicts when task references message_ids."""
        task = dict(task)
        raw = dict(task.get("data") or {})
        ids_raw = raw.get("message_ids")
        if ids_raw is not None and isinstance(ids_raw, list):
            want = {str(i) for i in ids_raw}
            by_id = {
                str(m.get("message_id")): m
                for m in all_messages
                if isinstance(m, dict) and m.get("message_id") is not None
            }
            raw["messages"] = [by_id[i] for i in want if i in by_id]
        task["data"] = raw
        return task

    def process_with_orchestrator(self, messages: List[Dict]) -> Dict[str, Any]:
        """
        Orchestrator plans (grouping + tasks); GenericAgent executes each task.
        """
        print(
            "\nOrchestrator–worker pipeline: planner proposes grouping + worker queue; "
            "each worker returns structured JSON artifacts."
        )
        print(f"Inbound batch size: {len(messages)} SWIFT-shaped dict(s).\n")

        print("Planner: calling Orchestrator.analyze_and_create_tasks() ...")
        planner = self.Orchestrator(self.client, self.model)
        plan = planner.analyze_and_create_tasks(messages)

        analysis = plan.get("analysis", "")
        self._log_phase("Planner", self._compact(f"Synopsis → {analysis}", 240))

        gp = plan.get("grouping_plan") or {}
        dim = gp.get("group_by", "?")
        self._log_phase(
            "Grouping",
            self._compact(
                f"dimension={dim} | rationale={gp.get('rationale', '')}", 260
            ),
        )
        gprev = gp.get("groups_preview")
        if isinstance(gprev, list) and gprev:
            preview = ", ".join(
                str(item.get("group_key", "?"))
                for item in gprev[:8]
                if isinstance(item, dict)
            )
            self._log_phase("Groups-preview", preview or "(empty keys)")

        tasks = plan.get("tasks") or []
        declared = plan.get("task_count", len(tasks))
        self._log_phase("Queue", f"task_count={declared}; executing {len(tasks)} task(s)\n")

        worker = self.GenericAgent(self.client, self.model)
        results: List[Dict[str, Any]] = []

        for i, task in enumerate(tasks, start=1):
            tid = task.get("task_id", f"idx{i}")
            ttype = task.get("type", "?")
            pri = task.get("priority", "")
            desc = task.get("description", "")
            print(f"Worker {i}/{len(tasks)}: START {tid} | type={ttype} priority={pri}")
            self._log_phase("Brief", self._compact(desc, 220))

            task = self._inject_message_subset(task, messages)

            out = worker.execute_task(task)
            results.append(out)

            st = out.get("status")
            headline = self._compact(out.get("headline") or "(no headline)", 180)
            nfind = (
                len(out["findings"])
                if isinstance(out.get("findings"), list)
                else "?"
            )
            self._log_phase(
                "Done",
                f"status={st} | headline={headline} | findings_count={nfind}",
            )

        summary = (
            f"Planner emitted {len(tasks)} worker task(s) for batch n={len(messages)}; "
            f"{sum(1 for r in results if r.get('status') == 'completed')}/"
            f"{max(len(results), 1)} completed without transport errors."
        )
        package = {
            "orchestrator_analysis": plan,
            "task_results": results,
            "summary": summary,
        }
        print(f"\n{summary}")
        return package

    def test_orchestrator(self) -> Dict[str, Any]:
        """Smoke test mirroring Udacity scaffolding messages."""
        test_messages = [
            {
                "message_id": "MSG001",
                "message_type": "MT103",
                "amount": "75000.00 USD",
                "sender_bic": "CHASUS33XXX",
                "receiver_bic": "DEUTDEFFXXX",
                "reference": "TRX20240101001",
                "remittance_info": "Payment for equipment purchase",
            },
            {
                "message_id": "MSG002",
                "message_type": "MT202",
                "amount": "1000000.00 EUR",
                "sender_bic": "BNPAFRPPXXX",
                "receiver_bic": "BARCGB22XXX",
                "reference": "COV20240101002",
                "remittance_info": "Cover payment",
            },
        ]

        print("=== Orchestrator-Worker smoke run ===")
        bundle = self.process_with_orchestrator(test_messages)

        print("\n=== Worker headlines (replay) ===")
        for row in bundle.get("task_results", []):
            if not isinstance(row, dict):
                continue
            headline = row.get("headline", "")
            self._log_phase(
                str(row.get("task_id")),
                self._compact(f'{row.get("status")} — {headline}', 260),
            )
        print("=== Smoke run END ===")

        return bundle


class TestHelper:
    """Lightweight helpers for breakpoint debugging."""

    @staticmethod
    def test_orchestrator_only() -> Dict[str, Any]:
        print("Isolation: Orchestrator only")
        ow = OrchestratorWorkerPattern()
        orch = OrchestratorWorkerPattern.Orchestrator(ow.client, ow.model)
        msgs = [{"message_id": "ISO1", "message_type": "MT103", "amount": "100 USD"}]
        plan = orch.analyze_and_create_tasks(msgs)
        OrchestratorWorkerPattern._log_phase("tasks-only", json.dumps(plan)[:280])
        return plan

    @staticmethod
    def test_generic_agent_only() -> Dict[str, Any]:
        print("Isolation: GenericAgent only")
        ow = OrchestratorWorkerPattern()
        sample_task = {
            "task_id": "test_001",
            "type": "compliance_check",
            "description": "Check if sender BIC is valid format",
            "data": {"sender_bic": "CHASUS33XXX"},
        }
        agent = OrchestratorWorkerPattern.GenericAgent(ow.client, ow.model)
        return agent.execute_task(sample_task)


if __name__ == "__main__":
    pattern = OrchestratorWorkerPattern()
    pattern.test_orchestrator()
