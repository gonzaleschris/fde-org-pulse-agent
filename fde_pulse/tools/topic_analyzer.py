"""Topic and Positive Wins Analyzer Tool with LLM Function Calling."""
from typing import List, Optional
from ..models.schemas import ChatMessage, HotTopic, PositiveWin
from ..services.llm_client import GeminiLLMClient

class TopicAndWinsAnalyzerTool:
    """Tool to extract emerging technical patterns and celebrate customer wins using Gemini 2.0."""

    def __init__(self, llm_client: Optional[GeminiLLMClient] = None):
        self.llm_client = llm_client or GeminiLLMClient()

    def analyze_topics(self, messages: List[ChatMessage]) -> List[HotTopic]:
        """Extracts and synthesizes trending technical topics from chat messages.
        
        Args:
            messages: List of sanitized ChatMessage objects.

        Returns:
            List of structured HotTopic instances.
        """
        combined_text = "\n".join([f"[{m.sender} ({m.role})]: {m.content}" for m in messages])
        prompt = (
            f"Analyze the following internal FDE team chat messages from 'AI GTM Tech - All Team':\n\n"
            f"{combined_text}\n\n"
            f"Extract the top emerging technical topic, including title, category, mentions count, "
            f"concise summary, impact level, and key contributors."
        )
        system_inst = "You are an expert FDE technical lead summarizing emerging AI agent patterns."
        
        topic = self.llm_client.generate_structured(
            prompt=prompt,
            system_instruction=system_inst,
            response_schema=HotTopic,
            task_type="extraction"
        )
        return [topic]

    def analyze_wins(self, messages: List[ChatMessage]) -> List[PositiveWin]:
        """Extracts customer deployment wins and milestone accomplishments.
        
        Args:
            messages: List of sanitized ChatMessage objects.

        Returns:
            List of structured PositiveWin instances.
        """
        combined_text = "\n".join([f"[{m.sender} ({m.role})]: {m.content}" for m in messages])
        prompt = (
            f"Review the following FDE chat messages and extract positive customer wins or milestones:\n\n"
            f"{combined_text}\n\n"
            f"Provide the headline, target customer/project, accomplishment description, lead engineers, "
            f"and quantifiable impact metrics."
        )
        system_inst = "You are an FDE engagement manager extracting verified customer deployment milestones."
        
        win = self.llm_client.generate_structured(
            prompt=prompt,
            system_instruction=system_inst,
            response_schema=PositiveWin,
            task_type="extraction"
        )
        return [win]

    # Aliases for backward compatibility
    extract_hot_topics = analyze_topics
    extract_positive_wins = analyze_wins
