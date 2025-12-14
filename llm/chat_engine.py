from typing import List, Dict, Optional
import json
from datetime import datetime
from config.settings import Settings
from vector_db.chroma_manager import ChromaDBManager
from vector_db.embeddings import LocalEmbeddings
from .prompts import PromptTemplates

# Import based on configuration
if Settings.USE_OLLAMA:
    import ollama
else:
    from groq import Groq

class TradingAssistant:
    """Main chat engine for trading analysis using FREE LLMs"""
    
    def __init__(self):
        # Initialize LLM
        if Settings.USE_OLLAMA:
            self.llm_client = ollama
            print(f"Using Ollama with model: {Settings.OLLAMA_MODEL}")
        else:
            self.llm_client = Groq(api_key=Settings.GROQ_API_KEY)
            print(f"Using Groq with model: {Settings.LLM_MODEL}")
        
        # Initialize other components
        self.chroma_manager = ChromaDBManager()
        self.embedding_generator = LocalEmbeddings()
        self.prompt_templates = PromptTemplates()
    
    def get_response(self,
                    query: str,
                    tickers: List[str] = None,
                    doc_types: List[str] = None,
                    date_range: tuple = None,
                    mode: str = "Comprehensive",
                    top_k: int = 5) -> Dict:
        """Generate response using RAG pipeline"""
        
        try:
            # Step 1: Generate query embedding
            print("Generating query embedding...")
            query_embedding = self.embedding_generator.generate_embedding(query)
            
            # Step 2: Build search filters
            filters = {}
            if tickers:
                filters['tickers'] = tickers
            if doc_types:
                filters['doc_types'] = doc_types
            
            # Step 3: Search for relevant documents
            print("Searching for relevant documents...")
            retrieved_docs = self.chroma_manager.search(
                query_embedding=query_embedding,
                filters=filters,
                top_k=top_k
            )
            
            # Step 4: Prepare context
            context = self._prepare_context(retrieved_docs)
            
            # Step 5: Get system prompt
            system_prompt = self.prompt_templates.get_system_prompt(mode)
            
            # Step 6: Generate response with LLM
            print("Generating response...")
            
            if Settings.USE_OLLAMA:
                # Ollama response
                response = ollama.chat(
                    model=Settings.OLLAMA_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": self.prompt_templates.format_user_prompt(query, context)}
                    ]
                )
                analysis = response['message']['content']
            else:
                # Groq response
                chat_completion = self.llm_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": self.prompt_templates.format_user_prompt(query, context)}
                    ],
                    model=Settings.LLM_MODEL,
                    temperature=Settings.TEMPERATURE,
                    max_tokens=Settings.MAX_TOKENS
                )
                analysis = chat_completion.choices[0].message.content
            
            # Step 7: Extract trading signals
            signals = self._extract_trading_signals(analysis, tickers)
            
            # Step 8: Format response
            formatted_response = {
                'analysis': analysis,
                'sources': self._format_sources(retrieved_docs),
                'signals': signals,
                'metadata': {
                    'query': query,
                    'mode': mode,
                    'documents_retrieved': len(retrieved_docs),
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            return formatted_response
            
        except Exception as e:
            print(f"Error in get_response: {e}")
            return {
                'analysis': f"Error processing request: {str(e)}",
                'sources': [],
                'signals': [],
                'metadata': {'error': str(e)}
            }
    
    def _prepare_context(self, docs: List[Dict]) -> str:
        """Prepare context from retrieved documents"""
        
        if not docs:
            return "No relevant documents found."
        
        context_parts = []
        
        for i, doc in enumerate(docs[:5], 1):  # Limit context for free models
            metadata = doc.get('metadata', {})
            
            context_part = f"""
Document {i}:
Company: {metadata.get('ticker', 'Unknown')} - {metadata.get('company_name', '')}
Type: {metadata.get('document_type', 'Unknown')}
Content: {doc.get('text', 'No content')}
"""
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _format_sources(self, docs: List[Dict]) -> List[Dict]:
        """Format source documents for display"""
        
        sources = []
        
        for doc in docs:
            metadata = doc.get('metadata', {})
            
            source = {
                'ticker': metadata.get('ticker', 'Unknown'),
                'type': metadata.get('document_type', 'Unknown'),
                'date': metadata.get('date', 'Unknown'),
                'relevance_score': doc.get('score', 0),
                'snippet': doc.get('text', '')[:200] + '...'
            }
            
            sources.append(source)
        
        return sources
    
    def _extract_trading_signals(self, analysis: str, tickers: List[str] = None) -> List[Dict]:
        """Extract trading signals from analysis"""
        
        signals = []
        
        # Keywords for signal detection
        bullish_keywords = ['bullish', 'buy', 'upside', 'growth', 'positive']
        bearish_keywords = ['bearish', 'sell', 'downside', 'risk', 'negative']
        
        analysis_lower = analysis.lower()
        
        if tickers:
            for ticker in tickers[:5]:  # Limit to 5 tickers
                if ticker.lower() in analysis_lower:
                    # Count keywords
                    bullish_score = sum(1 for kw in bullish_keywords if kw in analysis_lower)
                    bearish_score = sum(1 for kw in bearish_keywords if kw in analysis_lower)
                    
                    if bullish_score > bearish_score:
                        signals.append({
                            'ticker': ticker,
                            'direction': 'bullish',
                            'confidence': min(bullish_score / 5, 1.0),
                            'reason': 'Positive indicators detected'
                        })
                    elif bearish_score > bullish_score:
                        signals.append({
                            'ticker': ticker,
                            'direction': 'bearish',
                            'confidence': min(bearish_score / 5, 1.0),
                            'reason': 'Risk factors detected'
                        })
        
        return signals