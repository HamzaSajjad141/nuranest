import time
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from .agents import PregnancyHealthAgent
from .models import QuestionResponse
from .config import settings

logger = logging.getLogger(__name__)

class PregnancyAIService:
    """Service layer for Pregnancy AI operations"""
    
    def __init__(self):
        self.agent: Optional[PregnancyHealthAgent] = None
        self.is_initialized = False
        self.initialization_error = None
        
    async def initialize(self) -> bool:
        """Initialize the AI service"""
        try:
            logger.info("🚀 Initializing Pregnancy AI Service...")
            self.agent = PregnancyHealthAgent()
            
            # Initialize the system
            success = self.agent.initialize_system()
            if success:
                self.is_initialized = True
                logger.info("✅ Pregnancy AI Service initialized successfully")
                return True
            else:
                self.initialization_error = "Failed to initialize AI system"
                logger.error("❌ Failed to initialize AI system")
                return False
                
        except Exception as e:
            self.initialization_error = str(e)
            logger.error(f"❌ Error initializing service: {e}")
            return False
    
    async def ask_question(self, question: str) -> QuestionResponse:
        """Process a pregnancy health question"""
        start_time = time.time()
        
        try:
            if not self.is_initialized or not self.agent:
                raise Exception("AI service not initialized")
            
            # Log the question
            logger.info(f"Question: {question}")
            
            # Process the question
            answer = self.agent.process_question(question)
            
            # Extract sources for terminal logging only
            sources = await self._extract_sources(question)
            
            # Log sources to terminal
            if sources:
                logger.info("📚 Sources found:")
                for i, source in enumerate(sources[:3], 1):
                    logger.info(f"  {i}. {source}")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create response (without sources)
            response = QuestionResponse(
                answer=answer,
                confidence_score=0.9,  # Default confidence score
                processing_time=processing_time,
                timestamp=datetime.now(),
                sources=sources
            )
            
            logger.info(f"✅ Question processed successfully in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Error processing question: {e}")
            
            # Return error response
            return QuestionResponse(
                answer=f"Sorry, I encountered an error while processing your question: {str(e)}",
                sources=[],
                confidence_score=0.0,
                processing_time=processing_time,
                timestamp=datetime.now()
            )
    
    async def _extract_sources(self, query: str) -> List[str]:
        """Extract sources from the last search operation for terminal logging"""
        sources = []
        
        try:
            if not self.agent or not self.agent.retriever:
                return sources
            
            # Get documents from retriever
            docs = self.agent.retriever.invoke(query)
            
            for i, doc in enumerate(docs[:3], 1):
                source = doc.metadata.get('source', 'Unknown source')
                filename = source.split('/')[-1] if '/' in source else source
                filename = filename.split('\\')[-1] if '\\' in filename else filename
                sources.append(filename)
                
        except Exception as e:
            logger.error(f"Error extracting sources: {e}")
        
        return sources

# Global service instance
pregnancy_service = PregnancyAIService() 