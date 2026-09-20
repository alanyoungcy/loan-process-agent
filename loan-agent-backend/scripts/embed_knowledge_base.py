#!/usr/bin/env python3
"""
Knowledge Base Embedding Script
Embeds HK regulations and documents into ChromaDB
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any
import hashlib

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.genai.vector_store import get_vector_store
from app.services.genai.llm_client import get_llm_client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentChunker:
    """Chunk documents for embedding"""

    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Chunk text into overlapping segments

        Args:
            text: Text to chunk
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks

        Returns:
            List of chunk dicts
        """
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for delimiter in ['. ', '。', '\n\n', '\n']:
                    last_delim = text[start:end].rfind(delimiter)
                    if last_delim > chunk_size * 0.7:  # At least 70% of chunk
                        end = start + last_delim + len(delimiter)
                        break

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'start': start,
                    'end': end
                })

            start = end - overlap

        return chunks


class KnowledgeBaseEmbedder:
    """Embed knowledge base documents into ChromaDB"""

    def __init__(self):
        self.vector_store = get_vector_store()
        self.llm_client = get_llm_client()
        self.chunker = DocumentChunker()
        self.knowledge_base_dir = Path(__file__).parent.parent.parent / "rag" / "knowledge_base"

    async def embed_compliance_documents(self):
        """Embed HK compliance regulations"""
        logger.info("Embedding compliance documents...")

        # Create collection
        self.vector_store.create_collection("compliance_policies")

        documents = []
        metadatas = []
        ids = []

        # Load HK regulation documents
        files = [
            {
                "path": "Money_Lenders_Ordinance_Cap163.txt",
                "source": "Money Lenders Ordinance (Cap. 163)",
                "type": "legislation"
            },
            {
                "path": "LMLA_Code_of_Money_Lending_Practice.txt",
                "source": "LMLA Code of Money Lending Practice",
                "type": "code_of_practice"
            },
            {
                "path": "PDPO_Cap486.txt",
                "source": "Personal Data (Privacy) Ordinance (Cap. 486)",
                "type": "legislation"
            }
        ]

        for file_info in files:
            file_path = self.knowledge_base_dir / file_info["path"]

            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                continue

            logger.info(f"Processing {file_info['source']}...")

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Chunk document
            chunks = self.chunker.chunk_text(content, chunk_size=500, overlap=50)

            for i, chunk in enumerate(chunks):
                chunk_id = hashlib.md5(
                    f"{file_info['path']}-{i}".encode()
                ).hexdigest()

                documents.append(chunk['text'])
                metadatas.append({
                    'source': file_info['source'],
                    'type': file_info['type'],
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                })
                ids.append(chunk_id)

            logger.info(f"Created {len(chunks)} chunks from {file_info['source']}")

        # Add to vector store
        logger.info(f"Adding {len(documents)} chunks to compliance_policies collection...")
        self.vector_store.add_documents(
            collection_name="compliance_policies",
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        logger.info(f"✓ Embedded {len(documents)} compliance document chunks")

    async def embed_script_templates(self):
        """Embed approved script templates"""
        logger.info("Embedding script templates...")

        # Create collection
        self.vector_store.create_collection("script_templates")

        # Sample approved templates (in production, load from database)
        templates = [
            {
                "scenario": "first_contact",
                "content": """您好，我是XX銀行貸後服務部的[姓名]，請問是[客戶姓名]先生/女士嗎？

打擾您了。根據我們的記錄，您有一筆貸款逾期[X]天，金額為HK$[金額]。請問您什麼時候方便還款？

我們理解您可能遇到一些困難。如果您需要協商還款計劃，我們可以為您提供幫助。

感謝您的配合，祝您生活愉快。""",
                "effectiveness_score": 0.85,
                "language": "zh-HK"
            },
            {
                "scenario": "payment_plan",
                "content": """Thank you for discussing your situation with us.

Based on your current circumstances, we can offer you a structured payment plan:
- Monthly installment: HK$[amount]
- Duration: [X] months
- Start date: [date]

This plan will help you clear your outstanding balance while managing your cash flow. Does this work for you?

Please note this is a one-time accommodation to help you get back on track.""",
                "effectiveness_score": 0.78,
                "language": "en"
            },
            {
                "scenario": "payment_reminder",
                "content": """您好，這是XX銀行的還款提醒。

您的貸款還款日期為[日期]，金額為HK$[金額]。

如已安排還款，請忽略此訊息。如有任何疑問，請致電我們的客戶服務熱線。

謝謝！""",
                "effectiveness_score": 0.90,
                "language": "zh-HK"
            },
            {
                "scenario": "dispute_resolution",
                "content": """Thank you for raising your concerns about this account.

I understand you believe there may be an error. Let me help you resolve this:

1. I'll escalate your case to our disputes team
2. They will review your account within 3-5 business days
3. You will receive a written response

In the meantime, no further collection actions will be taken on this account.

May I have your email address to send you a reference number?""",
                "effectiveness_score": 0.82,
                "language": "en"
            },
            {
                "scenario": "final_notice",
                "content": """Dear [Customer Name],

This is a final notice regarding your overdue account [Account No.].

Outstanding amount: HK$[amount]
Due since: [date]
Days overdue: [X] days

If we do not receive payment by [deadline date], we will have no choice but to:
- Report this to credit reference agencies
- Commence legal proceedings

To avoid these consequences, please contact us immediately at [phone] or arrange payment online.

We remain willing to discuss payment arrangements.

Yours sincerely,
[Bank Name] Collections Team""",
                "effectiveness_score": 0.70,
                "language": "en"
            }
        ]

        documents = []
        metadatas = []
        ids = []

        for i, template in enumerate(templates):
            template_id = hashlib.md5(
                f"template-{template['scenario']}-{i}".encode()
            ).hexdigest()

            documents.append(template['content'])
            metadatas.append({
                'scenario': template['scenario'],
                'effectiveness_score': template['effectiveness_score'],
                'language': template['language']
            })
            ids.append(template_id)

        # Add to vector store
        self.vector_store.add_documents(
            collection_name="script_templates",
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        logger.info(f"✓ Embedded {len(templates)} script templates")

    async def embed_objection_responses(self):
        """Embed customer objection handling responses"""
        logger.info("Embedding objection responses...")

        # Create collection
        self.vector_store.create_collection("customer_objections")

        # Common objections and effective responses
        objections = [
            {
                "objection_type": "financial_hardship",
                "objection": "I don't have money right now, I lost my job",
                "response": """I understand this is a difficult time for you. Let's explore options:

1. Can you make a partial payment for now?
2. Would you like to discuss a temporary payment reduction?
3. What amount could you manage monthly?

We want to help you through this period while protecting your credit rating.""",
                "success_rate": 0.75
            },
            {
                "objection_type": "dispute_charges",
                "objection": "These charges are wrong, I already paid",
                "response": """I apologize for the confusion. Let me help clarify:

1. Could you provide the payment date and amount?
2. Do you have a receipt or transaction reference?
3. I'll check our system immediately

If there's been an error on our part, we'll correct it right away and apologize for any inconvenience.""",
                "success_rate": 0.88
            },
            {
                "objection_type": "request_more_time",
                "objection": "Can you give me until next month?",
                "response": """I appreciate you reaching out. Let me see what we can do.

- When exactly next month could you pay?
- Can you commit to a specific date?
- Would you be able to make a small payment today as a good faith gesture?

I'll note your commitment in our system, but I need a firm date from you.""",
                "success_rate": 0.82
            },
            {
                "objection_type": "threatens_bankruptcy",
                "objection": "I'm going to declare bankruptcy anyway",
                "response": """I understand you're considering that option. Before you make that decision:

1. Bankruptcy has serious long-term consequences
2. It may not be necessary for your situation
3. Have you spoken to a financial counselor?

Let's explore alternatives that won't impact your credit for 7-10 years. Many of our customers find payment arrangements more beneficial.""",
                "success_rate": 0.65
            },
            {
                "objection_type": "threatens_complaint",
                "objection": "I'm going to report you for harassment",
                "response": """I apologize if you feel we've contacted you excessively. That's certainly not our intention.

Let me help ensure this doesn't happen:
1. I'll note your preferred contact method and frequency
2. What time and channel works best for you?
3. How often would you like us to follow up?

Our goal is to work with you respectfully to resolve this matter.""",
                "success_rate": 0.70
            }
        ]

        documents = []
        metadatas = []
        ids = []

        for i, obj in enumerate(objections):
            obj_id = hashlib.md5(
                f"objection-{obj['objection_type']}-{i}".encode()
            ).hexdigest()

            # Combine objection and response for context
            full_text = f"Objection: {obj['objection']}\n\nResponse: {obj['response']}"

            documents.append(full_text)
            metadatas.append({
                'objection_type': obj['objection_type'],
                'success_rate': obj['success_rate']
            })
            ids.append(obj_id)

        # Add to vector store
        self.vector_store.add_documents(
            collection_name="customer_objections",
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        logger.info(f"✓ Embedded {len(objections)} objection responses")

    async def create_case_history_collection(self):
        """Create empty case history collection (populated during runtime)"""
        logger.info("Creating case_history collection...")

        self.vector_store.create_collection("case_history")

        logger.info("✓ Created case_history collection (to be populated at runtime)")

    async def verify_collections(self):
        """Verify all collections are created and populated"""
        logger.info("\nVerifying collections...")

        collections = [
            "compliance_policies",
            "script_templates",
            "customer_objections",
            "case_history"
        ]

        for collection_name in collections:
            try:
                count = self.vector_store.get_collection_count(collection_name)
                logger.info(f"✓ {collection_name}: {count} documents")
            except Exception as e:
                logger.error(f"✗ {collection_name}: {str(e)}")

    async def run(self):
        """Run full embedding pipeline"""
        logger.info("Starting knowledge base embedding pipeline...")

        try:
            await self.embed_compliance_documents()
            await self.embed_script_templates()
            await self.embed_objection_responses()
            await self.create_case_history_collection()
            await self.verify_collections()

            logger.info("\n✓ Knowledge base embedding complete!")

        except Exception as e:
            logger.error(f"✗ Embedding failed: {str(e)}", exc_info=True)
            raise


async def main():
    """Main entry point"""
    embedder = KnowledgeBaseEmbedder()
    await embedder.run()


if __name__ == "__main__":
    asyncio.run(main())
