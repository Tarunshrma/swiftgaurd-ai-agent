"""
SWIFT Transaction Processing System with Agent Patterns
Main application entry point

This is the main integration point where all agent patterns work together
to process SWIFT messages through a complete pipeline.
"""

from typing import List, Dict, Any

from config import Config
from services.swift_generator import SWIFTGenerator

# Import the agent patterns you'll be using
from agents.evaluator_optimizer import EvaluatorOptimizerPattern
from agents.parallelization import ParallelizationPattern
from agents.orchestrator_worker import OrchestratorWorkerPattern
from agents.prompt_chaining import PromptChainingPattern


class SWIFTProcessingSystem:
    """Main system orchestrating all agent patterns for SWIFT processing"""

    def __init__(self):
        self.config = Config()
        self.swift_generator = SWIFTGenerator()

        # Initialize agent patterns
        # NOTE: These classes are scaffolded in the agents folder
        # You'll need to complete the TODOs in each file for them to work properly
        self.evaluator_optimizer = EvaluatorOptimizerPattern()
        self.parallelization_agent = ParallelizationPattern()
        self.orchestrator_worker = OrchestratorWorkerPattern()
        self.prompt_chaining_agent = PromptChainingPattern()
    
    def generate_swift_messages(self) -> List[Dict[str, Any]]:
        """Generate SWIFT messages as plain dicts for downstream agents."""
        models = self.swift_generator.generate_messages(
            count=self.config.MESSAGE_COUNT,
            bank_count=self.config.BANK_COUNT,
        )
        out: List[Dict[str, Any]] = []
        for m in models:
            d = m.model_dump(mode="json")
            # Evaluator reads currency from the amount string (e.g. "15000.00 USD").
            amt, cur = d.get("amount"), d.get("currency")
            if amt is not None and cur and " " not in str(amt):
                d["amount"] = f"{amt} {cur}"
            out.append(d)
        return out
    
    def process_with_evaluator_optimizer(self, messages: List[Dict]) -> List[Dict]:
        """
        Step 1: Validate and correct SWIFT messages using Evaluator-Optimizer pattern

        This method calls the evaluator optimizer pattern to validate and fix messages.
        """
        print("\n" + "=" * 60)
        print("STEP 1: EVALUATOR-OPTIMIZER PATTERN")
        print("=" * 60)

        # Call the evaluator optimizer's process method
        validated_messages = self.evaluator_optimizer.process_with_evaluator_optimizer(messages)
        return validated_messages

    def process_with_parallelization(self, messages: List[Dict]) -> List[Dict]:
        """
        Step 2: Process messages in parallel with fraud detection

        This method uses parallel processing to run multiple fraud detection agents.
        """
        print("\n" + "=" * 60)
        print("STEP 2: PARALLELIZATION PATTERN")
        print("=" * 60)

        # Process messages in parallel using fraud detection agents
        processed_messages = self.parallelization_agent.process_batch_parallel(messages)
        return processed_messages

    def process_with_prompt_chaining(self, messages: List[Dict]) -> Dict:
        """
        Step 3: Enhanced fraud analysis using Prompt Chaining pattern

        This method chains multiple AI agents for comprehensive fraud analysis.
        """
        print("\n" + "=" * 60)
        print("STEP 3: PROMPT CHAINING PATTERN")
        print("=" * 60)

        # Process through the chain of agents
        chain_results = self.prompt_chaining_agent.process_chain(messages)
        return chain_results

    def process_with_orchestrator_worker(self, messages: List[Dict]) -> None:
        """
        Step 4: Process transactions using Orchestrator-Worker pattern

        This method uses an orchestrator to create tasks and workers to execute them.
        """
        print("\n" + "=" * 60)
        print("STEP 4: ORCHESTRATOR-WORKER PATTERN")
        print("=" * 60)

        # TODO 5: Two distinct orchestrator report runs (different filters).
        non_fraud = [
            msg for msg in messages if msg.get("fraud_status") != "FRAUDULENT"
        ]
        fraud_only = [
            msg for msg in messages if msg.get("fraud_status") == "FRAUDULENT"
        ]

        print("\n--- Report set 1: non-fraudulent messages (CLEAN / not FRAUDULENT) ---")
        print(f"Selected {len(non_fraud)} message(s).")
        if non_fraud:
            self.orchestrator_worker.process_with_orchestrator(non_fraud)
        else:
            print("No messages in this set; skipping orchestrator.")

        print("\n--- Report set 2: fraud-flagged messages only ---")
        print(f"Selected {len(fraud_only)} message(s).")
        if fraud_only:
            self.orchestrator_worker.process_with_orchestrator(fraud_only)
        else:
            print("No fraudulent messages in this batch; skipping orchestrator.")

    
    def run(self):
        """Main execution method - Orchestrates all agent patterns in sequence"""
        try:
            print("=" * 60)
            print("SWIFT TRANSACTION PROCESSING SYSTEM")
            print("=" * 60)

            # Step 1: Generate SWIFT messages
            print("\nGenerating SWIFT messages...")
            messages = self.generate_swift_messages()
            print(f"Generated {len(messages)} SWIFT messages")

            validated_messages = self.process_with_evaluator_optimizer(messages)
            processed_messages = self.process_with_parallelization(validated_messages)
            self.process_with_prompt_chaining(processed_messages)
            self.process_with_orchestrator_worker(processed_messages)

            print("\n" + "=" * 60)
            print("PROCESSING COMPLETE")
            print("=" * 60)

        except Exception as e:
            print(f"Error in main execution: {e}")
            raise


if __name__ == "__main__":
    system = SWIFTProcessingSystem()
    system.run()
