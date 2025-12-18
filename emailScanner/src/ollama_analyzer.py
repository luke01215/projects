"""
Ollama integration for analyzing emails and making delete/keep recommendations.
Uses local LLM models for privacy and cost-effectiveness.
Includes few-shot learning from past human decisions.
"""
import json
import logging
from typing import Dict, Optional, List
import requests

logger = logging.getLogger(__name__)


class OllamaAnalyzer:
    """AI email analyzer using Ollama local models"""
    
    def __init__(self, base_url: str = 'http://localhost:11434', model: str = 'llama3.2', db_session=None):
        """
        Initialize Ollama analyzer
        
        Args:
            base_url: Ollama API base URL
            model: Model name to use (e.g., 'llama3.2', 'mistral', 'llama2')
            db_session: Database session for few-shot learning (optional)
        """
        self.base_url = base_url
        self.model = model
        self.api_url = f"{base_url}/api/generate"
        self.db_session = db_session
        
    def check_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                logger.info(f"Connected to Ollama. Available models: {model_names}")
                
                # Check if model exists (exact match or with :latest tag)
                model_found = False
                if self.model in model_names:
                    model_found = True
                elif f"{self.model}:latest" in model_names:
                    # Auto-append :latest tag if model exists with that tag
                    self.model = f"{self.model}:latest"
                    logger.info(f"Using model: {self.model}")
                    model_found = True
                
                if not model_found:
                    logger.warning(f"Model '{self.model}' not found. Available: {model_names}")
                    return False
                return True
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return False
    
    def analyze_email(self, email_data: Dict) -> Optional[Dict]:
        """
        Analyze an email and provide recommendation
        
        Args:
            email_data: Dictionary with email fields (sender, subject, body, etc.)
        
        Returns:
            Dictionary with analysis results or None if failed
        """
        try:
            # Get similar past decisions for few-shot learning
            examples = self._get_few_shot_examples(email_data)
            
            # Build context for the AI (with examples if available)
            prompt = self._build_analysis_prompt(email_data, examples)
            
            # Call Ollama API
            logger.info(f"Analyzing email from {email_data.get('sender', 'unknown')}")
            if examples:
                logger.info(f"  Using {len(examples)} past decisions as examples")
            response = self._call_ollama(prompt)
            
            if not response:
                return None
            
            # Parse AI response
            analysis = self._parse_analysis_response(response)
            
            # Add model metadata
            analysis['model_name'] = self.model
            analysis['model_version'] = 'latest'
            
            logger.info(f"Analysis complete: {analysis['recommendation']} (confidence: {analysis['confidence_score']:.2f})")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze email: {e}")
            return None
    
    def _get_few_shot_examples(self, email_data: Dict) -> List[Dict]:
        """Get relevant past decisions for few-shot learning"""
        if not self.db_session:
            return []
        
        try:
            from sender_memory import SenderMemory
            memory = SenderMemory(self.db_session)
            
            # Get up to 3 similar past decisions
            examples = memory.get_similar_decisions(
                email_data.get('sender', ''),
                email_data.get('category', 'unknown'),
                limit=3
            )
            
            return examples
        except Exception as e:
            logger.warning(f"Failed to get few-shot examples: {e}")
            return []
    
    def _build_analysis_prompt(self, email_data: Dict, examples: List[Dict] = None) -> str:
        """Build the prompt for email analysis with optional few-shot examples"""
        sender = email_data.get('sender', 'Unknown')
        subject = email_data.get('subject', 'No subject')
        body_preview = email_data.get('body_preview', '')[:500]
        has_attachments = email_data.get('has_attachments', False)
        received_date = email_data.get('date', 'Unknown')
        
        # Calculate email age
        from datetime import datetime, UTC
        age_days = None
        age_description = "Unknown"
        if received_date != 'Unknown':
            try:
                if isinstance(received_date, str):
                    email_date = datetime.fromisoformat(received_date.replace('Z', '+00:00'))
                else:
                    email_date = received_date
                age_days = (datetime.now(UTC) - email_date).days
                if age_days == 0:
                    age_description = "Today"
                elif age_days == 1:
                    age_description = "Yesterday"
                elif age_days < 7:
                    age_description = f"{age_days} days old"
                elif age_days < 30:
                    weeks = age_days // 7
                    age_description = f"{weeks} week{'s' if weeks > 1 else ''} old"
                elif age_days < 365:
                    months = age_days // 30
                    age_description = f"{months} month{'s' if months > 1 else ''} old"
                else:
                    years = age_days // 365
                    age_description = f"{years} year{'s' if years > 1 else ''} old"
            except:
                pass
        
        prompt = f"""You are an email classification assistant. Analyze this email and provide a recommendation.

Email Details:
- From: {sender}
- Subject: {subject}
- Date: {received_date}
- Age: {age_description}
- Has attachments: {has_attachments}
- Body preview: {body_preview}"""

        # Add few-shot examples if available
        if examples:
            prompt += "\n\nPrevious decisions you made for similar emails:\n"
            for ex in examples:
                decision = "kept" if ex['human_decision'] == 'keep' else "deleted"
                subject_preview = ex['subject'][:50] + "..." if len(ex['subject']) > 50 else ex['subject']
                prompt += f"- From {ex['sender']}: \"{subject_preview}\" → You {decision} it (Category: {ex['category']})\n"

        prompt += """

Task: Analyze this email and provide:
1. Recommendation: Should this email be "delete", "keep", or "archive"?
2. Confidence: Your confidence level (0.0 to 1.0)
3. Reasoning: Brief explanation for your recommendation
4. Category: Email category (e.g., "newsletter", "personal", "promotional", "notification", "spam", "important", "job_offer", "recruiter")
5. Priority: Priority level ("low", "medium", "high")

Guidelines:
- Recommend "delete" for: 
  * Spam and unsolicited emails
  * Old newsletters (more than a week old) - REGARDLESS of source reputation (NASA, news sites, etc.)
  * Promotional/sale emails from companies (especially if older than 30-60 days)
  * Job offers and recruiter emails (especially if old or unsolicited)
  * Automated notifications with no value
  * Mass marketing emails
  * Old transactional emails (receipts, confirmations older than 90 days)
  * Any bulk/broadcast email that is more than 7 days old
  
- Consider email age carefully:
  * Recent emails (< 7 days): Be more conservative, might still be relevant
  * Medium age (7-30 days): Normal evaluation - newsletters/promotional should be deleted
  * Old emails (30-60 days): More aggressive deletion for promotional/newsletter content
  * Very old emails (60+ days): Very aggressive deletion unless personal/important
  
- Newsletter indicators (should be deleted if > 7 days old):
  * Generic "newsletter" format with multiple articles/sections
  * Mass-sent emails with unsubscribe links
  * Automated digest emails
  * Regular updates from organizations (even reputable ones like NASA, news sites)
  * Any email that feels like a broadcast rather than personal communication
  
- Recommend "keep" for: 
  * Personal correspondence from real people
  * Important business emails
  * Emails requiring action or response
  * Emails from family, friends, or close contacts
  
- Recommend "archive" for: 
  * Receipts and order confirmations
  * Reference materials that might be needed later
  * Travel confirmations and bookings
  * Important records and documentation

Recruiter/Job Email Indicators:
- Emails from recruiters or staffing agencies (e.g., @vdartinc.com, @teksystems.com, etc.)
- Subjects containing: "position", "role", "opportunity", "contract", "remote", "developer", "engineer"
- Language like: "immediate need", "hiring for", "seeking candidates", "job opening"
- Emails offering job positions or contract roles
→ These should be marked as "delete" with category "job_offer" or "recruiter"

Be conservative: if unsure, prefer "keep" or "archive" over "delete"
Higher confidence (>0.8) for clear spam/newsletters/recruiters, lower confidence (<0.6) for ambiguous emails

Respond in JSON format:
{{
    "recommendation": "delete|keep|archive",
    "confidence_score": 0.85,
    "reasoning": "Brief explanation here",
    "category": "newsletter",
    "priority": "low"
}}

Respond ONLY with valid JSON, no other text."""

        return prompt
    
    def _call_ollama(self, prompt: str, temperature: float = 0.3) -> Optional[str]:
        """
        Call Ollama API with the prompt
        
        Args:
            prompt: Analysis prompt
            temperature: Sampling temperature (lower = more deterministic)
        
        Returns:
            AI response text or None if failed
        """
        try:
            payload = {
                'model': self.model,
                'prompt': prompt,
                'temperature': temperature,
                'stream': False
            }
            
            response = requests.post(self.api_url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error calling Ollama: {e}")
        
        return None
    
    def _parse_analysis_response(self, response: str) -> Dict:
        """
        Parse AI response and extract structured data
        
        Args:
            response: Raw AI response text
        
        Returns:
            Structured analysis dictionary
        """
        # Default fallback values
        default_analysis = {
            'recommendation': 'keep',
            'confidence_score': 0.5,
            'reasoning': 'Unable to parse AI response',
            'category': 'unknown',
            'priority': 'medium'
        }
        
        try:
            # Try to find JSON in the response
            response = response.strip()
            
            # Remove markdown code blocks if present
            if response.startswith('```'):
                lines = response.split('\n')
                response = '\n'.join(lines[1:-1])
            
            # Parse JSON
            analysis = json.loads(response)
            
            # Validate required fields
            if 'recommendation' not in analysis:
                logger.warning("Missing 'recommendation' in AI response")
                return default_analysis
            
            # Ensure recommendation is valid
            valid_recommendations = ['delete', 'keep', 'archive']
            if analysis['recommendation'] not in valid_recommendations:
                logger.warning(f"Invalid recommendation: {analysis['recommendation']}")
                analysis['recommendation'] = 'keep'
            
            # Ensure confidence is in valid range
            if 'confidence_score' in analysis:
                confidence = float(analysis['confidence_score'])
                analysis['confidence_score'] = max(0.0, min(1.0, confidence))
            else:
                analysis['confidence_score'] = 0.5
            
            # Fill in optional fields with defaults
            analysis.setdefault('reasoning', 'No reasoning provided')
            analysis.setdefault('category', 'unknown')
            analysis.setdefault('priority', 'medium')
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {response[:200]}")
        except Exception as e:
            logger.error(f"Error parsing analysis response: {e}")
        
        return default_analysis
    
    def batch_analyze(self, emails: list) -> list:
        """
        Analyze multiple emails in sequence
        
        Args:
            emails: List of email data dictionaries
        
        Returns:
            List of analysis results
        """
        results = []
        
        for i, email_data in enumerate(emails, 1):
            logger.info(f"Analyzing email {i}/{len(emails)}")
            analysis = self.analyze_email(email_data)
            
            if analysis:
                results.append({
                    'email_id': email_data.get('email_id'),
                    'analysis': analysis
                })
            else:
                logger.warning(f"Failed to analyze email {email_data.get('email_id')}")
        
        logger.info(f"Batch analysis complete: {len(results)}/{len(emails)} successful")
        return results


# Example usage and testing
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Initialize analyzer
    analyzer = OllamaAnalyzer(model='llama3.2')
    
    # Check connection
    if not analyzer.check_connection():
        print("Error: Cannot connect to Ollama. Make sure it's running with: ollama serve")
        exit(1)
    
    # Test with sample email
    sample_email = {
        'sender': 'newsletter@example.com',
        'subject': '50% OFF - Limited Time Offer!',
        'body_preview': 'Shop now and save big on all items. This offer expires soon!',
        'date': '2025-12-13',
        'has_attachments': False
    }
    
    print("\nAnalyzing sample email...")
    result = analyzer.analyze_email(sample_email)
    
    if result:
        print("\nAnalysis Result:")
        print(f"  Recommendation: {result['recommendation']}")
        print(f"  Confidence: {result['confidence_score']:.2f}")
        print(f"  Category: {result['category']}")
        print(f"  Priority: {result['priority']}")
        print(f"  Reasoning: {result['reasoning']}")
    else:
        print("Analysis failed!")
