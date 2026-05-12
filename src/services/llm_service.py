"""
LLM service for fraud analysis and SWIFT message correction using OpenAI
"""

import json
import logging
from typing import Dict, List, Any
import os

from openai import OpenAI
from models.swift_message import SWIFTMessage
from config import Config


class LLMService:
    """
    Service for LLM-based fraud analysis and SWIFT message correction
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = Config()
        
        # Initialize OpenAI client
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)
        self.model = self.config.OPENAI_MODEL
        
        self.logger.info(f"LLM Service initialized with model: {self.model}")
    
    def review_suspicious_transaction(self, message: SWIFTMessage, fraud_score: float, 
                                    indicators: List[str]) -> Dict[str, Any]:
        """
        Use LLM to review suspicious transactions and make hold/approve decisions
        """
        
        try:
            prompt = self._create_fraud_review_prompt(message, fraud_score, indicators)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert fraud analyst specializing in SWIFT transactions. "
                        "Analyze the provided transaction data and make a decision about whether to "
                        "approve, reject, or hold the transaction for further investigation. "
                        "Respond with JSON in the specified format."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1  # Low temperature for consistent analysis
            )
            
            result = json.loads(response.choices[0].message.content or "{}")
            
            self.logger.debug(f"LLM fraud review completed for {message.message_id}: {result['decision']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"LLM fraud review failed for {message.message_id}: {str(e)}")
            # Return conservative hold decision on error
            return {
                "decision": "HOLD",
                "confidence": 0.5,
                "reasoning": f"LLM analysis failed: {str(e)}",
                "risk_factors": indicators,
                "recommended_actions": ["Manual review required due to system error"]
            }
    
    def get_swift_correction(self, prompt: str) -> Dict[str, Any]:
        """
        Get SWIFT message corrections from LLM
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a SWIFT message validation expert. "
                        "Your task is to correct SWIFT message format errors while "
                        "maintaining the business intent of the transaction. "
                        "Respond with JSON containing the corrected fields."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content or "{}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"LLM SWIFT correction failed: {str(e)}")
            return {}
    
    def analyze_benford_deviation(self, amounts: List[float], deviation_score: float, 
                                p_value: float) -> Dict[str, Any]:
        """
        Use LLM to analyze Benford's Law deviations and provide insights
        """
        try:
            prompt = self._create_benford_analysis_prompt(amounts, deviation_score, p_value)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial forensics expert specializing in "
                        "Benford's Law analysis for fraud detection. Analyze the provided "
                        "transaction data and explain the significance of any deviations. "
                        "Respond with JSON in the specified format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content or "{}")
            
            self.logger.debug("LLM Benford's Law analysis completed")
            
            return result
            
        except Exception as e:
            self.logger.error(f"LLM Benford analysis failed: {str(e)}")
            return {
                "analysis": "Analysis failed",
                "significance": "UNKNOWN",
                "recommendations": ["Manual review required"]
            }
    
    def _create_fraud_review_prompt(self, message: SWIFTMessage, fraud_score: float, 
                                  indicators: List[str]) -> str:
        """
        Create prompt for LLM fraud review
        """
        prompt = f"""
Analyze the following SWIFT transaction for fraud risk:

TRANSACTION DETAILS:
- Message ID: {message.message_id}
- Type: {message.message_type}
- Reference: {message.reference}
- Amount: {message.amount} {message.currency}
- Sender BIC: {message.sender_bic}
- Receiver BIC: {message.receiver_bic}
- Value Date: {message.value_date}

AUTOMATED FRAUD ANALYSIS:
- Fraud Score: {fraud_score:.3f} (0.0 = no risk, 1.0 = high risk)
- Risk Indicators:
{chr(10).join(f"  - {indicator}" for indicator in indicators)}

ADDITIONAL CONTEXT:
- Ordering Customer: {getattr(message, 'ordering_customer', 'N/A')}
- Beneficiary: {getattr(message, 'beneficiary', 'N/A')}
- Remittance Info: {getattr(message, 'remittance_info', 'N/A')}

Based on this information, make a decision and provide analysis.

Respond with JSON in this exact format:
{{
    "decision": "APPROVE|HOLD|REJECT",
    "confidence": 0.0-1.0,
    "reasoning": "Detailed explanation of your decision",
    "risk_factors": ["list", "of", "key", "risk", "factors"],
    "recommended_actions": ["list", "of", "recommended", "actions"],
    "business_impact": "Assessment of business impact if decision is wrong",
    "additional_checks": ["list", "of", "additional", "checks", "recommended"]
}}

Decision Guidelines:
- APPROVE: Low risk, process normally
- HOLD: Medium risk, requires manual review
- REJECT: High risk, block transaction
"""
        return prompt
    
    def _create_benford_analysis_prompt(self, amounts: List[float], deviation_score: float, 
                                      p_value: float) -> str:
        """
        Create prompt for Benford's Law analysis
        """
        # Extract first digits for analysis
        first_digits = []
        for amount in amounts[:20]:  # Sample first 20 for prompt
            amount_str = str(int(amount)).lstrip('0')
            if amount_str and amount_str[0].isdigit():
                first_digits.append(int(amount_str[0]))
        
        prompt = f"""
Analyze the following transaction data for Benford's Law compliance:

DATASET OVERVIEW:
- Total Transactions: {len(amounts)}
- Sample First Digits: {first_digits[:20]}
- Sample Amounts: {[f"${amt:,.2f}" for amt in amounts[:10]]}

STATISTICAL ANALYSIS:
- Deviation Score: {deviation_score:.4f}
- P-Value: {p_value:.6f}
- Significant Deviation: {p_value < 0.05}

BENFORD'S LAW CONTEXT:
Benford's Law states that in many real-world datasets, the first digit follows a specific distribution:
- Digit 1: ~30.1%
- Digit 2: ~17.6%
- Digit 3: ~12.5%
- etc.

Significant deviations may indicate:
- Data manipulation
- Systematic fraud
- Artificial data generation
- Specific business processes

Respond with JSON in this exact format:
{{
    "analysis": "Detailed analysis of the deviation and its implications",
    "significance": "LOW|MEDIUM|HIGH",
    "fraud_probability": 0.0-1.0,
    "likely_causes": ["list", "of", "likely", "causes"],
    "recommendations": ["list", "of", "recommended", "actions"],
    "false_positive_risk": "Assessment of false positive risk",
    "additional_analysis": "Suggestions for additional analysis"
}}
"""
        return prompt
    
    def batch_analyze_transactions(self, messages: List[SWIFTMessage]) -> Dict[str, Any]:
        """
        Perform batch analysis of multiple transactions for patterns
        """
        try:
            # Create summary of transaction patterns
            amounts = [float(msg.amount) for msg in messages]
            currencies = [msg.currency for msg in messages]
            bics = [(msg.sender_bic, msg.receiver_bic) for msg in messages]
            
            prompt = f"""
Analyze this batch of {len(messages)} SWIFT transactions for suspicious patterns:

SUMMARY STATISTICS:
- Total Transactions: {len(messages)}
- Amount Range: ${min(amounts):,.2f} - ${max(amounts):,.2f}
- Average Amount: ${sum(amounts)/len(amounts):,.2f}
- Unique Currencies: {len(set(currencies))}
- Unique BIC Pairs: {len(set(bics))}

SAMPLE TRANSACTIONS:
{chr(10).join([
    f"- {msg.message_type} {msg.amount} {msg.currency} {msg.sender_bic}->{msg.receiver_bic}"
    for msg in messages[:10]
])}

Look for patterns that might indicate:
- Systematic fraud
- Money laundering schemes  
- Structuring activities
- Coordination between entities

Respond with JSON format analysis of suspicious patterns found.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial crimes investigator analyzing "
                        "transaction patterns for suspicious activity."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content or "{}")
            
            self.logger.info("LLM batch analysis completed")
            
            return result
            
        except Exception as e:
            self.logger.error(f"LLM batch analysis failed: {str(e)}")
            return {
                "analysis": "Batch analysis failed",
                "patterns": [],
                "recommendations": ["Manual review required"]
            }
