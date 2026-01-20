import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load env vars first
load_dotenv()

# Add backend to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.lark_client import LarkClient
from rich.console import Console
from rich.table import Table

console = Console()

async def verify_lark_data():
    console.print("[bold cyan]🔍 Verifying Lark Data Integrity...[/bold cyan]")
    
    client = LarkClient()
    
    # 1. Fetch all records (paginated) to get count
    console.print("Fetching records from Lark...")
    # NOTE: list_records might be paginated or limited. 
    # Let's try to fetch a reasonable number or check if there is a count method (usually not in basic client)
    # We will fetch up to 1000 to verify the night shift's ~230 records.
    
    try:
        # Load ID from env
        app_token = os.getenv("LARK_BASE_TOKEN")
        table_id = os.getenv("LARK_TABLE_ID")
        
        if not app_token or not table_id:
            console.print("[red]❌ Error: LARK_BASE_TOKEN or LARK_TABLE_ID not set in .env[/red]")
            return

        # Handle list_records return format (it might return a dict with 'items' or similar)
        # Based on previous LarkClient code, it likely returns the raw JSON response or items list.
        # Let's verify the response structure.
        # NOTE: list_records seems to be sync based on error "object dict can't be used in 'await' expression"
        response = client.list_records(app_token=app_token, table_id=table_id, page_size=500) 
        
        # Check if response is list or dict
        if isinstance(response, dict):
            records = response.get('items', [])
            if not records and 'data' in response:
                 records = response['data'].get('items', [])
        else:
             records = response # Assume it returned list directly if wrapper simplified it
             
        total_count = len(records)
        
        console.print(f"✅ Total Records Fetched: [bold green]{total_count}[/bold green]")
        
        if total_count < 200:
            console.print("[yellow]⚠️ Warning: Record count is lower than expected (~230 from night shift).[/yellow]")
        else:
            console.print("[green]✅ Record count matches expectations.[/green]")

        if records:
            console.print(f"[dim]Debug: First record keys: {records[0].keys()}[/dim]")
            if 'fields' in records[0]:
                 console.print(f"[dim]Debug: First record fields: {records[0]['fields'].keys()}[/dim]")
            else:
                 console.print(f"[red]Debug: 'fields' key missing in record: {records[0]}[/red]")

        # 2. Check quality of recent records
        table = Table(title="Recent 5 Records Sample")
        table.add_column("Snippet Type", style="cyan")
        table.add_column("Quality", style="magenta")
        table.add_column("Content Preview", style="green")
        
        for record in records[:5]:
            fields = record.get("fields", {})
            
            # Map Chinese keys if needed
            snippet_type = fields.get("snippet_type") or fields.get("类型") or "N/A"
            quality = fields.get("quality_score") or fields.get("质量评分") or fields.get("评分") or "N/A"
            content = fields.get("clean_text") or fields.get("正文") or fields.get("内容") or ""
            
            table.add_row(
                str(snippet_type),
                str(quality),
                str(content)[:50] + "..."
            )
            
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]❌ Error fetching records: {e}[/red]")

if __name__ == "__main__":
    asyncio.run(verify_lark_data())
