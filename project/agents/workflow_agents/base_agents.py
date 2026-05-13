"""
Base Agent Classes for SWIFT Transaction Processing

This module contains the base classes that all agents inherit from.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from config import Config
from services.llm_service import LLMService


class BaseAgent(ABC):
    """Shared config and LLM service for agents that speak to OpenAI."""

    def __init__(self) -> None:
        self.config = Config()
        self.llm_service = LLMService()

    @abstractmethod
    def create_prompt(self, data: Any) -> str:
        """Format the user-facing instruction text passed into the LLM."""

    def respond(self, prompt: str) -> Dict[str, Any]:
        """
        Run SWIFT correction with JSON object mode.

        Parsing and ``response_format`` are implemented once in ``LLMService.get_swift_correction``
        (covers TODO logic for structured output without duplicating it here).
        """
        return self.llm_service.get_swift_correction(prompt)


class SwiftCorrectionAgent(BaseAgent):
    """Optimizer side of evaluator–optimizer: fix invalid SWIFT-shaped dicts."""

    def create_prompt(self, data: Any) -> str:
        """
        Build the user prompt. ``data`` is a dict with ``message`` and ``errors`` keys.
        The system-role expert text stays in ``LLMService.get_swift_correction``.
        """
        message = data.get("message")
        errors = data.get("errors", [])
        return (
            f"Original SWIFT Message:\n{message}\n\n"
            f"Validation Errors to Fix:\n{errors}\n\n"
            "Return one JSON object with the full corrected SWIFT message "
            "(e.g. message_type, reference, amount as a string with currency "
            "like '5000.00 USD', sender_bic, receiver_bic, value_date, "
            "remittance_info / ordering_customer / beneficiary when present)."
        )

    def respond(self, message: Dict[str, Any], errors: List[str]) -> Dict[str, Any]:
        """
        Public API used by ``EvaluatorOptimizerPattern.optimize_message``.

        Implements the course optimizer: call model, parse JSON to dict,
        fall back to the original dict on failure or empty reply.
        """
        try:
            prompt = self.create_prompt({"message": message, "errors": errors})
            result = super().respond(prompt)
            return result if result else message
        except Exception as e:
            print(f"Error in SwiftCorrectionAgent: {e}")
            return message


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