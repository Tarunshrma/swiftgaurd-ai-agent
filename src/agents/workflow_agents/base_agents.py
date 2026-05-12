"""
Base Agent Classes for SWIFT Transaction Processing

This module contains the base classes that all agents inherit from.
You will implement the BaseAgent abstract class and the SwiftCorrectionAgent.
"""

# TODO 6: Create BaseAgent abstract class (10 points)
# INSTRUCTIONS:
# 1. Import ABC and abstractmethod from the abc module
# 2. Create a BaseAgent class that inherits from ABC
# 3. The class should have:
#    - An __init__ method that initializes self.config and self.llm_service
#    - An abstract method create_prompt(self, data) that returns a string
#    - A concrete method respond(self, prompt) that calls the LLM service
#
# HINT: Look at how the solution implements agent classes in the lessons
# EXAMPLE STRUCTURE:
"""
from abc import ABC, abstractmethod
from config import Config
from services.llm_service import LLMService

class BaseAgent(ABC):
    def __init__(self):
        self.config = Config()
        self.llm_service = # Initialize LLMService here

    @abstractmethod
    def create_prompt(self, data):
        '''Each agent must implement your own prompt creation'''
        pass

    def respond(self, prompt: str):
        '''Common method to get LLM response'''
        # Use self.llm_service to get response
        pass
"""

# YOUR CODE HERE - Implement BaseAgent class


class SwiftCorrectionAgent:
    """Agent for correcting SWIFT messages based on validation errors."""

    def __init__(self):
        # TODO 7: Define LLMService (5 points)
        # INSTRUCTIONS: Initialize self.llm_service with an instance of LLMService
        # HINT: from services.llm_service import LLMService
        # Then: self.llm_service = LLMService()

        pass  # Remove this pass after adding your code

    def create_prompt(self, message, errors):
        """
        Create a prompt for the LLM to correct a SWIFT message.

        Args:
            message: The SWIFT message data
            errors: List of validation errors to fix

        Returns:
            str: The formatted prompt for the LLM
        """
        system_prompt = """You are a SWIFT message correction expert.
        Fix the validation errors while maintaining the business intent.
        Return the corrected message in JSON format."""

        user_prompt = f"""
        Original SWIFT Message:
        {message}

        Validation Errors to Fix:
        {errors}

        Please correct these errors and return the complete corrected message in JSON format.
        """

        return system_prompt, user_prompt

    def respond(self, message, errors):
        """
        Get LLM response to correct the SWIFT message.

        Args:
            message: The SWIFT message to correct
            errors: The validation errors to fix

        Returns:
            dict: The corrected message data
        """
        import json
        from openai import OpenAI

        system_prompt, user_prompt = self.create_prompt(message, errors)

        try:
            client = OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                # TODO 8: Set response format (3 points)
                # INSTRUCTIONS: Add the response_format parameter to ensure JSON output
                # The format should be: response_format={"type": "json_object"}
                # This ensures the LLM returns valid JSON that we can parse

                temperature=0.1
            )

            # TODO 9: Parse response result (2 points)
            # INSTRUCTIONS: Extract and parse the JSON content from the response
            # HINT: The response content is in response.choices[0].message.content
            # You'll need to:
            # 1. Get the content from response.choices[0].message.content
            # 2. Use json.loads() to parse it into a Python dictionary
            # 3. Return the parsed result

            # Example:
            # content = response.choices[0].message.content
            # result = json.loads(content)
            # return result

            return {}  # Replace with parsed response

        except Exception as e:
            print(f"Error in SwiftCorrectionAgent: {e}")
            return message  # Return original if correction fails


class FraudAmountDetectionAgent:
    """Agent for detecting fraud based on transaction amounts."""

    def __init__(self):
        self.rules = [
            {"condition": "amount > 10000", "risk_score": 0.3},
            {"condition": "round_amount", "risk_score": 0.2},
            {"condition": "unusual_precision", "risk_score": 0.1}
        ]

    def analyze(self, message):
        """
        Analyze a SWIFT message for amount-based fraud patterns.

        Args:
            message: The SWIFT message to analyze

        Returns:
            dict: Fraud analysis results with risk score and reasons
        """
        risk_score = 0
        fraud_reasons = []

        try:
            # Extract amount from message
            amount_str = message.get('amount', '0')
            # Remove currency code and convert to float
            amount = float(''.join(c for c in amount_str if c.isdigit() or c == '.'))

            # Rule 1: Large amounts
            if amount > 10000:
                risk_score += 0.3
                fraud_reasons.append(f"High amount transaction: {amount}")

            # Rule 2: Round amounts (multiples of 1000)
            if amount % 1000 == 0 and amount > 0:
                risk_score += 0.2
                fraud_reasons.append(f"Suspiciously round amount: {amount}")

            # Rule 3: Unusual precision for large amounts
            if amount > 100000 and (amount % 1) != 0:
                risk_score += 0.1
                fraud_reasons.append("Large amount with unusual decimal precision")

        except (ValueError, TypeError) as e:
            print(f"Error analyzing amount: {e}")

        return {
            "agent": "FraudAmountDetectionAgent",
            "risk_score": min(risk_score, 1.0),
            "fraud_reasons": fraud_reasons
        }


class FraudPatternDetectionAgent:
    """Agent for detecting fraud based on transaction patterns."""

    def __init__(self):
        self.high_risk_patterns = ['TEST', 'FAKE', 'DEMO', '999', '000000']
        self.suspicious_keywords = ['urgent', 'immediately', 'secret', 'confidential']

    def analyze(self, message):
        """
        Analyze a SWIFT message for pattern-based fraud indicators.

        Args:
            message: The SWIFT message to analyze

        Returns:
            dict: Fraud analysis results with risk score and reasons
        """
        risk_score = 0
        fraud_reasons = []

        # Check BIC codes for test patterns
        sender_bic = message.get('sender_bic', '')
        receiver_bic = message.get('receiver_bic', '')

        for pattern in self.high_risk_patterns:
            if pattern in sender_bic.upper() or pattern in receiver_bic.upper():
                risk_score += 0.4
                fraud_reasons.append(f"Test/fake pattern detected in BIC: {pattern}")

        # Check for same sender and receiver
        if sender_bic and sender_bic == receiver_bic:
            risk_score += 0.5
            fraud_reasons.append("Same sender and receiver BIC")

        # Check remittance info for suspicious keywords
        remittance = message.get('remittance_info', '').lower()
        for keyword in self.suspicious_keywords:
            if keyword in remittance:
                risk_score += 0.2
                fraud_reasons.append(f"Suspicious keyword in remittance: {keyword}")

        return {
            "agent": "FraudPatternDetectionAgent",
            "risk_score": min(risk_score, 1.0),
            "fraud_reasons": fraud_reasons
        }


class FraudAggAgent:
    """Agent for aggregating fraud detection results from multiple agents."""

    def __init__(self):
        self.threshold = 0.5  # Fraud threshold (50%)

    def aggregate_results(self, fraud_results):
        """
        Aggregate fraud detection results from multiple agents.

        Args:
            fraud_results: List of fraud detection results from different agents

        Returns:
            dict: Aggregated fraud assessment
        """
        if not fraud_results:
            return {
                "is_fraudulent": False,
                "confidence": 0,
                "total_risk_score": 0,
                "aggregated_reasons": []
            }

        # Calculate average risk score
        total_risk = sum(r.get('risk_score', 0) for r in fraud_results)
        avg_risk = total_risk / len(fraud_results)

        # Aggregate all fraud reasons
        all_reasons = []
        for result in fraud_results:
            agent_name = result.get('agent', 'Unknown')
            reasons = result.get('fraud_reasons', [])
            for reason in reasons:
                all_reasons.append(f"[{agent_name}] {reason}")

        # Determine if fraudulent based on threshold
        is_fraudulent = avg_risk >= self.threshold

        return {
            "is_fraudulent": is_fraudulent,
            "confidence": round(avg_risk * 100, 2),
            "total_risk_score": round(avg_risk, 3),
            "aggregated_reasons": all_reasons
        }