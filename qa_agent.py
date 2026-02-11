"""Question Answering Agent using retrieved documents and LLM."""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from config import AppConfig, LLMConfig
from retriever import SemanticSearchEngine, RetrievedDocument
from utils import TextCleaner, logger


@dataclass
class QAResult:
    """Result of a question answering operation."""
    question: str
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    retrieved_docs_count: int


class LLMInterface:
    """Abstract interface for LLM interactions."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
    
    def generate(self, prompt: str, context: str = "") -> str:
        """Generate text using the LLM."""
        raise NotImplementedError
    
    def query(self, question: str, context: str) -> str:
        """Answer a question given context."""
        prompt = self._build_qa_prompt(question, context)
        return self.generate(prompt)
    
    @staticmethod
    def _build_qa_prompt(question: str, context: str) -> str:
        """Build a QA prompt."""
        return f"""Based on the following context, answer the question:

Context:
{context}

Question: {question}

Answer:"""


class OpenAIInterface(LLMInterface):
    """OpenAI API interface."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        try:
            import openai
            openai.api_key = config.api_key
            self.client = openai.OpenAI(api_key=config.api_key)
            logger.info(f"Initialized OpenAI client for model: {config.model_name}")
        except ImportError:
            logger.error("openai package not installed")
            raise
    
    def generate(self, prompt: str, context: str = "") -> str:
        """Generate text using OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful research assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


class LocalLLMInterface(LLMInterface):
    """Interface for local/offline LLMs."""
    
    def generate(self, prompt: str, context: str = "") -> str:
        """Simple fallback for demonstration."""
        logger.info("Using fallback response (no LLM configured)")
        return "This is a placeholder response. Configure an LLM provider to generate real answers."


def get_llm_interface(config: LLMConfig) -> LLMInterface:
    """Factory function to get the appropriate LLM interface."""
    if config.provider.lower() == "openai":
        if not config.api_key:
            logger.warning("OpenAI API key not configured. Using fallback.")
            return LocalLLMInterface(config)
        return OpenAIInterface(config)
    elif config.provider.lower() == "anthropic":
        logger.warning("Anthropic support not yet implemented. Using fallback.")
        return LocalLLMInterface(config)
    else:
        logger.warning(f"Unknown LLM provider: {config.provider}. Using fallback.")
        return LocalLLMInterface(config)


class ResearchAssistantAgent:
    """Main agent for research and question answering."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.search_engine = SemanticSearchEngine(config)
        self.llm = get_llm_interface(config.llm)
        self.conversation_history: List[Dict[str, str]] = []
    
    def answer_question(
        self,
        question: str,
        top_k: Optional[int] = None,
        use_context: bool = True
    ) -> QAResult:
        """Answer a question using semantic search and LLM."""
        logger.info(f"Processing question: {question}")
        
        # Search for relevant documents
        search_results = self.search_engine.search(question, top_k=top_k or self.config.top_k)
        
        if not search_results and use_context:
            logger.warning("No relevant documents found")
            answer = "I could not find relevant information to answer your question."
            confidence = 0.0
        else:
            # Build context from search results
            context = self._build_context(search_results)
            
            # Generate answer using LLM
            answer = self.llm.query(question, context)
            
            # Calculate confidence based on number of sources and similarity scores
            confidence = self._calculate_confidence(search_results)
        
        # Create result
        result = QAResult(
            question=question,
            answer=answer,
            sources=self._extract_sources(search_results),
            confidence=confidence,
            retrieved_docs_count=len(search_results)
        )
        
        # Add to conversation history
        from datetime import datetime
        self.conversation_history.append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def _build_context(self, documents: List[RetrievedDocument]) -> str:
        """Build context string from retrieved documents."""
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(
                f"[Source {i}: {doc.source}]\n{TextCleaner.truncate(doc.text, 400)}\n"
            )
        return "\n".join(context_parts)
    
    @staticmethod
    def _extract_sources(documents: List[RetrievedDocument]) -> List[Dict[str, Any]]:
        """Extract source information from documents."""
        sources = []
        seen_sources = set()
        
        for doc in documents:
            source_key = f"{doc.source}::{doc.chunk_id}"
            if source_key not in seen_sources:
                sources.append({
                    "source": doc.source,
                    "chunk_id": doc.chunk_id,
                    "similarity": round(doc.similarity, 4),
                })
                seen_sources.add(source_key)
        
        return sources
    
    @staticmethod
    def _calculate_confidence(documents: List[RetrievedDocument]) -> float:
        """Calculate confidence score based on search results."""
        if not documents:
            return 0.0
        
        # Average similarity of top results
        avg_similarity = sum(d.similarity for d in documents) / len(documents)
        
        # Confidence based on number of sources and similarity
        source_factor = min(len(documents) / 3, 1.0)  # Normalize to 0-1
        similarity_factor = avg_similarity
        
        confidence = (source_factor + similarity_factor) / 2
        return round(confidence, 4)
    
    def interactive_chat(self) -> None:
        """Run interactive chat session."""
        logger.info("Starting interactive chat session")
        print("\n" + "="*80)
        print("AI Research Assistant - Interactive Mode")
        print("Type 'quit' to exit, 'clear' to clear history")
        print("="*80 + "\n")
        
        while True:
            try:
                question = input("You: ").strip()
                
                if not question:
                    continue
                elif question.lower() == 'quit':
                    print("Exiting...")
                    break
                elif question.lower() == 'clear':
                    self.conversation_history.clear()
                    print("Conversation history cleared.\n")
                    continue
                
                # Get answer
                result = self.answer_question(question)
                
                # Display result
                print(f"\nAssistant: {result.answer}\n")
                print(f"Confidence: {result.confidence:.2%} | Sources: {result.retrieved_docs_count}\n")
                
                if result.sources:
                    print("Sources:")
                    for source in result.sources:
                        print(f"  - {source['source']} (chunk {source['chunk_id']}, similarity: {source['similarity']})")
                    print()
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                logger.error(f"Error processing question: {e}")
                print(f"Error: {str(e)}\n")
    
    def batch_answer(self, questions: List[str]) -> List[QAResult]:
        """Answer multiple questions."""
        results = []
        for question in questions:
            try:
                result = self.answer_question(question)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to answer '{question}': {e}")
        
        return results
