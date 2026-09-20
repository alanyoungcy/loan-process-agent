"""
Background Worker for GenAI Tasks
Processes async GenAI operations from RabbitMQ
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.database import get_db
from app.models.case import Case, GenAIAudit
from app.services.mq.rabbitmq_client import MessageQueueClient
from app.services.genai.summarizer import SummarizerService
from app.services.genai.script_generator import ScriptGenerator
from app.services.genai.intent_analyzer import IntentAnalyzer
from app.services.genai.willingness_scorer import WillingnessScorer
import redis.asyncio as redis

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GenAIWorker:
    """Worker for processing GenAI tasks from queue"""

    def __init__(self):
        self.mq_client = MessageQueueClient()
        self.redis_client = None
        self.summarizer = SummarizerService()
        self.script_generator = ScriptGenerator()
        self.intent_analyzer = IntentAnalyzer()
        self.willingness_scorer = WillingnessScorer()

    async def connect(self):
        """Connect to RabbitMQ and Redis"""
        await self.mq_client.connect()

        # Connect to Redis
        self.redis_client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

        logger.info("Worker connected to RabbitMQ and Redis")

    async def process_summarization_task(self, task_data: dict) -> dict:
        """
        Process case summarization task

        Args:
            task_data: Task data with case_id

        Returns:
            Summary result
        """
        case_id = task_data["payload"]["case_id"]

        logger.info(f"Processing summarization for case {case_id}")

        try:
            # Fetch case from database
            async for db in get_db():
                case = await db.get(Case, case_id)

                if not case:
                    raise ValueError(f"Case {case_id} not found")

                # Generate summary
                summary = await self.summarizer.summarize(case)

                # Store result in Redis (1 hour TTL)
                await self.redis_client.setex(
                    f"task:{task_data['task_id']}:result",
                    3600,
                    str(summary)
                )

                # Update task status
                await self.redis_client.setex(
                    f"task:{task_data['task_id']}:status",
                    3600,
                    "completed"
                )

                logger.info(f"Completed summarization for case {case_id}")

                return summary

        except Exception as e:
            logger.error(f"Error processing summarization: {str(e)}")

            # Update task status to failed
            await self.redis_client.setex(
                f"task:{task_data['task_id']}:status",
                3600,
                "failed"
            )

            raise

    async def process_script_generation_task(self, task_data: dict) -> dict:
        """
        Process script generation task

        Args:
            task_data: Task data with case_data and scenario

        Returns:
            Generated script
        """
        payload = task_data["payload"]
        case_data = payload["case_data"]
        scenario = payload.get("scenario", "general")

        logger.info(f"Processing script generation for scenario {scenario}")

        try:
            # Generate script
            script = await self.script_generator.generate_script(
                case_data=case_data,
                scenario=scenario
            )

            # Store result in Redis
            await self.redis_client.setex(
                f"task:{task_data['task_id']}:result",
                3600,
                str(script)
            )

            await self.redis_client.setex(
                f"task:{task_data['task_id']}:status",
                3600,
                "completed"
            )

            logger.info(f"Completed script generation for scenario {scenario}")

            return script

        except Exception as e:
            logger.error(f"Error processing script generation: {str(e)}")

            await self.redis_client.setex(
                f"task:{task_data['task_id']}:status",
                3600,
                "failed"
            )

            raise

    async def process_intent_analysis_task(self, task_data: dict) -> dict:
        """
        Process intent analysis task

        Args:
            task_data: Task data with conversation text

        Returns:
            Intent analysis result
        """
        conversation = task_data["payload"]["conversation"]

        logger.info("Processing intent analysis")

        try:
            # Analyze intent
            analysis = await self.intent_analyzer.analyze_intent(conversation)

            # Store result
            await self.redis_client.setex(
                f"task:{task_data['task_id']}:result",
                3600,
                str(analysis)
            )

            await self.redis_client.setex(
                f"task:{task_data['task_id']}:status",
                3600,
                "completed"
            )

            logger.info("Completed intent analysis")

            return analysis

        except Exception as e:
            logger.error(f"Error processing intent analysis: {str(e)}")

            await self.redis_client.setex(
                f"task:{task_data['task_id']}:status",
                3600,
                "failed"
            )

            raise

    async def process_batch_task(self, task_data: dict) -> dict:
        """
        Process batch summarization task

        Args:
            task_data: Task data with list of case_ids

        Returns:
            Batch results
        """
        case_ids = task_data["payload"]["case_ids"]

        logger.info(f"Processing batch task for {len(case_ids)} cases")

        results = []

        try:
            async for db in get_db():
                for case_id in case_ids:
                    try:
                        case = await db.get(Case, case_id)

                        if case:
                            summary = await self.summarizer.summarize(case)
                            results.append({
                                "case_id": case_id,
                                "success": True,
                                "summary": summary
                            })
                        else:
                            results.append({
                                "case_id": case_id,
                                "success": False,
                                "error": "Case not found"
                            })
                    except Exception as e:
                        logger.error(f"Error processing case {case_id}: {str(e)}")
                        results.append({
                            "case_id": case_id,
                            "success": False,
                            "error": str(e)
                        })

                # Store results
                await self.redis_client.setex(
                    f"task:{task_data['task_id']}:result",
                    3600,
                    str({"results": results})
                )

                await self.redis_client.setex(
                    f"task:{task_data['task_id']}:status",
                    3600,
                    "completed"
                )

                logger.info(f"Completed batch task: {len(results)} results")

                return {"results": results}

        except Exception as e:
            logger.error(f"Error processing batch task: {str(e)}")

            await self.redis_client.setex(
                f"task:{task_data['task_id']}:status",
                3600,
                "failed"
            )

            raise

    async def start_workers(self):
        """Start all worker queues"""
        logger.info("Starting GenAI workers...")

        # Create tasks for each queue
        tasks = [
            self.mq_client.consume_tasks(
                "genai.summarize",
                self.process_summarization_task
            ),
            self.mq_client.consume_tasks(
                "genai.script_generation",
                self.process_script_generation_task
            ),
            self.mq_client.consume_tasks(
                "genai.intent_analysis",
                self.process_intent_analysis_task
            ),
            self.mq_client.consume_tasks(
                "genai.batch_processing",
                self.process_batch_task
            ),
        ]

        # Run all workers concurrently
        await asyncio.gather(*tasks)

    async def shutdown(self):
        """Shutdown worker"""
        logger.info("Shutting down worker...")

        if self.redis_client:
            await self.redis_client.close()

        await self.mq_client.close()


async def main():
    """Main worker entry point"""
    worker = GenAIWorker()

    try:
        await worker.connect()
        await worker.start_workers()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Worker error: {str(e)}", exc_info=True)
    finally:
        await worker.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
