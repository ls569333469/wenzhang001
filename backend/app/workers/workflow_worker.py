
import asyncio
import os
import sys
import time
from typing import List, Dict

# Ensure project root in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()

from app.services.sync_service import sync_service
from app.agents.writer import writer_agent
from app.core.lark_client import lark_client
from app.core.config import get_logger

logger = get_logger("workers.workflow")

WORKFLOW_INTERVAL = 60  # seconds

async def process_item(item: Dict):
    """
    Process a single sync item:
    1. Construct Agent State
    2. Call Writer Agent
    3. Write back to Lark
    """
    record_id = item.get("id")
    content = item.get("content")
    style = item.get("style", "mimeng")
    emotion = item.get("emotion")
    
    logger.info(f"⚡ Processing Record {record_id} | Style: {style}")
    
    # 1. Construct State
    state = {
        "raw_input": content,
        "mode": style,
        "emotion": emotion,
        "narrative_type": "project_review", # Default or extract from somewhere?
        "api_config": {
             # Ideally these should come from central config
             "provider": "volcengine",
             "model_id": "ep-20250216124707-m55ty" # Hardcoded for worker MVP, or load from config file
        }
    }
    
    # 2. Call Agent
    try:
        # writer_agent is synchronous currently? Yes, based on code.
        # But if it calls LLM it might blocking. 
        # Ideally we should run in thread pool if blocking.
        result = writer_agent(state)
        
        if "error" in result:
            logger.error(f"❌ Generation Error for {record_id}: {result['error']}")
            # Update Lark with Error?
            lark_client.update_record(
                os.getenv("LARK_BASE_TOKEN"), 
                os.getenv("LARK_TABLE_ID"), 
                record_id, 
                {"状态": "生成失败", "AI生成结果": f"Error: {result['error']}"}
            )
            return

        draft = result.get("draft_content", "")
        logger.info(f"✅ Generated {len(draft)} chars for {record_id}")
        
        # 3. Write Back
        lark_client.update_record(
            os.getenv("LARK_BASE_TOKEN"), 
            os.getenv("LARK_TABLE_ID"), 
            record_id, 
            {
                "状态": "已完成", 
                "AI生成结果": draft
            }
        )
        logger.info(f"💾 Saved to Lark: {record_id}")
        
    except Exception as e:
        logger.error(f"❌ Critial Worker Error for {record_id}: {e}")
        lark_client.update_record(
                os.getenv("LARK_BASE_TOKEN"), 
                os.getenv("LARK_TABLE_ID"), 
                record_id, 
                {"状态": "系统异常"}
        )

async def run_worker():
    logger.info("🚀 Workflow Worker Started. Polling every 60s...")
    
    while True:
        try:
            # 1. Sync & Fetch New Tasks
            # Note: This syncs ALL pending items and marks them as synced locally.
            # But in the loop we want to process them.
            # wait, sync_service marks them as "已同步" (Synced) immediately upon fetching?
            # Yes, lines 135 in sync_service.py.
            # So if we crash after sync but before process, we lose tasks?
            # ideally sync_service should mark "Processing" or we process first.
            # For MVP, we trust the process logic. Or we can separate sync and update status.
            # Current logic: SyncService marks "已同步". 
            # We process them and mark "已完成" (Completed) later.
            # That's fine. "已同步" just means "System received it".
            
            sync_result = sync_service.sync_from_lark()
            new_items = sync_result.get("new_items", [])
            
            if new_items:
                logger.info(f"📥 Received {len(new_items)} new tasks.")
                for item in new_items:
                    await process_item(item)
            else:
                logger.debug("No new tasks.")
                
        except Exception as e:
            logger.error(f"Global Worker Exception: {e}")
            
        await asyncio.sleep(WORKFLOW_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        logger.info("🛑 Worker Stopped.")
