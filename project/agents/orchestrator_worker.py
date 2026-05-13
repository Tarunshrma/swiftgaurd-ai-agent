"""
Orchestrator-Worker Pattern for Task Distribution

This module implements the orchestrator-worker pattern where an orchestrator
breaks down work into tasks that are executed by generic workers.
"""

import json
from typing import Dict, List, Any
from openai import OpenAI
from config import Config


class OrchestratorWorkerPattern:
    """
    Implements the orchestrator-worker pattern for SWIFT message processing.
    The orchestrator analyzes messages and creates tasks for generic workers.
    """

    def __init__(self):
        """Initialize the orchestrator-worker pattern."""
        self.config = Config()
        self.client = OpenAI()
        self.model = "gpt-4o"

    # TODO 15: Create orchestrator (15 points)
    # INSTRUCTIONS:
    # This is the main TODO where you'll implement the complete orchestrator-worker pattern.
    # You need to:
    # 1. Create an Orchestrator class that analyzes messages and creates tasks
    # 2. Create a GenericAgent class that executes tasks
    # 3. Implement the process_with_orchestrator method to coordinate them
    #
    # DETAILED STEPS:
    #
    # Step 1: Create the Orchestrator class below this comment
    # The Orchestrator should:
    #   - Take a batch of messages
    #   - Analyze them and create a list of tasks
    #   - Return tasks with type and description
    #
    # Step 2: Create the GenericAgent class
    # The GenericAgent should:
    #   - Take a task (with type and description)
    #   - Execute the task according to its type
    #   - Return results
    #
    # Step 3: Implement process_with_orchestrator
    # This method should:
    #   - Create an orchestrator instance
    #   - Get tasks from the orchestrator
    #   - Create generic agent(s)
    #   - Execute tasks with the agents
    #   - Print/return results

    # YOUR CODE STARTS HERE

    class Orchestrator:
        """
        Orchestrator that analyzes messages and creates tasks for workers.

        HINT: This class should use the LLM to analyze messages and determine
        what tasks need to be performed.
        """

        def __init__(self):
            """Initialize the Orchestrator."""
            # Initialize OpenAI client
            # Set up any configuration needed
            pass

        def analyze_and_create_tasks(self, messages: List[Dict]) -> Dict:
            """
            Analyze messages and create tasks for workers.

            Args:
                messages: List of SWIFT messages to analyze

            Returns:
                Dictionary containing analysis and list of tasks

            HINT: Create a prompt that asks the LLM to:
            1. Analyze the batch of messages
            2. Identify what processing tasks are needed
            3. Return a structured list of tasks

            Example task structure:
            {
                "analysis": "Summary of the message batch",
                "tasks": [
                    {
                        "task_id": "task_001",
                        "type": "compliance_check",
                        "description": "Check sender BIC against sanctions list",
                        "priority": "high",
                        "data": {...}
                    },
                    {
                        "task_id": "task_002",
                        "type": "amount_analysis",
                        "description": "Analyze transaction amounts for patterns",
                        "priority": "medium",
                        "data": {...}
                    }
                ]
            }
            """
            # Create system prompt for orchestrator
            system_prompt = """You are an Orchestrator for SWIFT transaction processing.
            Analyze the provided messages and create specific tasks for workers.

            Task types you can create:
            - compliance_check: Check for regulatory compliance
            - fraud_analysis: Detailed fraud investigation
            - amount_verification: Verify and analyze amounts
            - pattern_detection: Detect unusual patterns
            - summary_report: Create summary reports

            Return JSON with your analysis and a list of specific tasks."""

            # Create user prompt with messages
            user_prompt = f"""Analyze these SWIFT messages and create processing tasks:

            {json.dumps(messages, indent=2)}

            Return JSON with structure:
            {{
                "analysis": "Your analysis of the message batch",
                "task_count": number,
                "tasks": [
                    {{
                        "task_id": "unique_id",
                        "type": "task_type",
                        "description": "What needs to be done",
                        "priority": "high|medium|low",
                        "data": "relevant data for the task"
                    }}
                ]
            }}"""

            # TODO: Call the LLM and return the response
            # Use self.client.chat.completions.create()
            # Don't forget response_format={"type": "json_object"}

            return {}  # Replace with actual implementation

    class GenericAgent:
        """
        Generic worker agent that executes tasks assigned by the orchestrator.

        HINT: This agent should be able to handle different task types
        and execute them accordingly.
        """

        def __init__(self):
            """Initialize the Generic Agent."""
            # Initialize OpenAI client
            # Set up any configuration needed
            pass

        def execute_task(self, task: Dict) -> Dict:
            """
            Execute a task assigned by the orchestrator.

            Args:
                task: Task dictionary with type, description, and data

            Returns:
                Dictionary with task results

            HINT: Based on the task type, create appropriate prompts
            and execute the task using the LLM.
            """
            task_type = task.get('type', 'unknown')
            description = task.get('description', '')
            task_data = task.get('data', {})

            # Create prompts based on task type
            if task_type == 'compliance_check':
                system_prompt = """You are a Compliance Specialist.
                Execute the compliance check as described."""
            elif task_type == 'fraud_analysis':
                system_prompt = """You are a Fraud Analyst.
                Perform detailed fraud analysis as requested."""
            elif task_type == 'amount_verification':
                system_prompt = """You are a Financial Auditor.
                Verify and analyze the amounts as specified."""
            elif task_type == 'pattern_detection':
                system_prompt = """You are a Pattern Analysis Expert.
                Detect and report unusual patterns."""
            elif task_type == 'summary_report':
                system_prompt = """You are a Report Generator.
                Create the requested summary report."""
            else:
                system_prompt = """You are a Generic Processing Agent.
                Complete the assigned task."""

            user_prompt = f"""Execute this task:
            Type: {task_type}
            Description: {description}
            Data: {json.dumps(task_data, indent=2)}

            Return your results in JSON format."""

            # TODO: Call the LLM and return the response
            # Use appropriate error handling

            return {
                "task_id": task.get('task_id'),
                "status": "completed",
                "results": "Task execution results here"
            }

    # YOUR CODE ENDS HERE

    def process_with_orchestrator(self, messages: List[Dict]) -> Dict:
        """
        Process messages using the orchestrator-worker pattern.

        Args:
            messages: List of SWIFT messages to process

        Returns:
            Processing results from the orchestrator-worker system

        TODO 15 IMPLEMENTATION:
        This method should:
        1. Create an Orchestrator instance
        2. Call analyze_and_create_tasks to get tasks
        3. Create one or more GenericAgent instances
        4. Execute each task using the generic agents
        5. Collect and return all results
        6. Print a summary of what was accomplished
        """
        print("=" * 60)
        print("ORCHESTRATOR-WORKER PATTERN PROCESSING")
        print("=" * 60)

        # Example structure (replace with your implementation):
        """
        # Step 1: Create orchestrator
        orchestrator = self.Orchestrator()

        # Step 2: Get tasks from orchestrator
        print("Orchestrator analyzing messages...")
        orchestrator_response = orchestrator.analyze_and_create_tasks(messages)

        print(f"Orchestrator Analysis: {orchestrator_response.get('analysis', 'No analysis')}")
        print(f"Tasks created: {orchestrator_response.get('task_count', 0)}")

        # Step 3: Create generic agent(s)
        agent = self.GenericAgent()

        # Step 4: Execute tasks
        results = []
        tasks = orchestrator_response.get('tasks', [])

        for task in tasks:
            print(f"Executing task: {task.get('task_id')} - {task.get('description')}")
            result = agent.execute_task(task)
            results.append(result)
            print(f"Task {task.get('task_id')} completed")

        # Step 5: Return results
        return {
            'orchestrator_analysis': orchestrator_response,
            'task_results': results,
            'summary': f"Processed {len(tasks)} tasks for {len(messages)} messages"
        }
        """

        # YOUR IMPLEMENTATION HERE
        # Remove the pass statement and implement the method
        pass

    def test_orchestrator(self):
        """
        Test method for the orchestrator-worker pattern.
        You can use this to verify your implementation.
        """
        test_messages = [
            {
                'message_id': 'MSG001',
                'message_type': 'MT103',
                'amount': '75000.00 USD',
                'sender_bic': 'CHASUS33XXX',
                'receiver_bic': 'DEUTDEFFXXX',
                'reference': 'TRX20240101001',
                'remittance_info': 'Payment for equipment purchase'
            },
            {
                'message_id': 'MSG002',
                'message_type': 'MT202',
                'amount': '1000000.00 EUR',
                'sender_bic': 'BNPAFRPPXXX',
                'receiver_bic': 'BARCGB22XXX',
                'reference': 'COV20240101002',
                'remittance_info': 'Cover payment'
            }
        ]

        print("Testing Orchestrator-Worker Pattern\n")
        results = self.process_with_orchestrator(test_messages)

        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)

        if results:
            print(f"Results obtained: {type(results)}")
            if isinstance(results, dict):
                for key, value in results.items():
                    print(f"{key}: {value if not isinstance(value, list) else f'{len(value)} items'}")

        return results


# Hint for You: You can test individual components
class TestHelper:
    """
    Helper class for testing individual components.
    You can use this to debug your implementations.
    """

    @staticmethod
    def test_orchestrator_only():
        """Test just the Orchestrator class."""
        print("Testing Orchestrator in isolation...")
        # Create an instance of the Orchestrator
        # Test with sample messages
        # Print the tasks it creates
        pass

    @staticmethod
    def test_generic_agent_only():
        """Test just the GenericAgent class."""
        print("Testing GenericAgent in isolation...")
        sample_task = {
            'task_id': 'test_001',
            'type': 'compliance_check',
            'description': 'Check if sender BIC is valid',
            'data': {'sender_bic': 'CHASUS33XXX'}
        }
        # Create an instance of GenericAgent
        # Execute the sample task
        # Print the results
        pass


if __name__ == "__main__":
    # Test the orchestrator-worker pattern
    # Note: Requires OPENAI_API_KEY environment variable
    pattern = OrchestratorWorkerPattern()
    pattern.test_orchestrator()

    # Uncomment to test individual components:
    # TestHelper.test_orchestrator_only()
    # TestHelper.test_generic_agent_only()