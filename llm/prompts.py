class PromptTemplates:
    """Prompt templates for different analysis modes"""
    
    def __init__(self):
        self.system_prompts = {
            "Comprehensive": """You are a financial analyst providing trading insights.
Analyze the provided financial data and give actionable recommendations.
Include key metrics, risks, and opportunities.""",

            "Quick Summary": """You are a financial analyst. Provide a brief summary
with only the most important trading insights in 2-3 sentences.""",

            "Risk-Focused": """You are a risk analyst. Focus on identifying
potential risks, red flags, and downside scenarios.""",

            "Growth-Focused": """You are a growth investor. Focus on
growth opportunities, positive catalysts, and upside potential."""
        }
    
    def get_system_prompt(self, mode: str) -> str:
        """Get system prompt for specified mode"""
        return self.system_prompts.get(mode, self.system_prompts["Comprehensive"])
    
    def format_user_prompt(self, query: str, context: str) -> str:
        """Format user prompt with query and context"""
        
        return f"""Question: {query}

Financial Data:
{context}

Please provide analysis based on the data above. Be specific and actionable."""