# automation/mcp_scheduler.py
import asyncio
import redis
import json
import schedule
import time
import subprocess
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class MCPTask:
    """Market Control Process Task"""
    id: str
    name: str
    command: str
    schedule_type: str  # 'interval', 'cron', 'market_hours'
    schedule_config: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    last_run: datetime = None
    next_run: datetime = None
    output: str = ""
    error: str = ""

class MarketDataCollector:
    """Automated market data collection"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.logger = logging.getLogger("MarketDataCollector")
    
    async def collect_market_data(self):
        """Run market data fetching scripts"""
        try:
            self.logger.info("🔄 Starting market data collection...")
            
            # Run the market news fetcher
            result = subprocess.run(
                ["python", "fetch_market_news.py"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.logger.info("✅ Market news fetched successfully")
                self.publish_status("market_data_success", {
                    "task": "fetch_market_news",
                    "output": result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout
                })
            else:
                self.logger.error(f"❌ Market news fetch failed: {result.stderr}")
                self.publish_status("market_data_error", {
                    "task": "fetch_market_news",
                    "error": result.stderr
                })
            
            # Run the hybrid price fetcher
            # Note: This should be running continuously, so we just check if it's alive
            await self.check_price_fetcher_health()
            
        except subprocess.TimeoutExpired:
            self.logger.error("⏰ Market data collection timed out")
        except Exception as e:
            self.logger.error(f"❌ Market data collection error: {e}")
    
    async def check_price_fetcher_health(self):
        """Check if the price fetcher is running"""
        try:
            # Check Redis for recent price updates
            last_event = self.redis_client.get("last_market_event")
            if last_event:
                event_data = json.loads(last_event)
                event_time = datetime.fromisoformat(event_data["timestamp"].replace("Z", "+00:00"))
                
                # If last event is more than 5 minutes old, restart the fetcher
                if datetime.utcnow() - event_time.replace(tzinfo=None) > timedelta(minutes=5):
                    self.logger.warning("⚠️ Price fetcher appears stale, attempting restart...")
                    await self.restart_price_fetcher()
                else:
                    self.logger.info("✅ Price fetcher is healthy")
            else:
                self.logger.warning("⚠️ No recent market events found")
                
        except Exception as e:
            self.logger.error(f"❌ Health check error: {e}")
    
    async def restart_price_fetcher(self):
        """Restart the price fetcher if it's not responding"""
        try:
            # Kill existing process (if any) and restart
            subprocess.run(["pkill", "-f", "market_data_fetcher.py"], capture_output=True)
            
            # Start new process in background
            subprocess.Popen(
                ["python", "market_data_fetcher.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.logger.info("🔄 Price fetcher restarted")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to restart price fetcher: {e}")
    
    def publish_status(self, status_type: str, data: Dict[str, Any]):
        """Publish status update to Redis"""
        status_event = {
            "type": status_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        self.redis_client.publish("mcp_status", json.dumps(status_event))
        self.redis_client.set("last_market_event", json.dumps(status_event), ex=300)  # 5 minute expiry

class PortfolioRebalancer:
    """Automated portfolio rebalancing"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.logger = logging.getLogger("PortfolioRebalancer")
        self.target_allocations = {
            "XAUUSD": 0.4,  # 40% Gold
            "XAGUSD": 0.3,  # 30% Silver
            "USDINDEX": 0.3  # 30% USD Index
        }
    
    async def rebalance_portfolio(self):
        """Rebalance portfolio based on target allocations"""
        try:
            self.logger.info("⚖️ Starting portfolio rebalancing...")
            
            # Get current portfolio state from Redis
            portfolio_data = self.redis_client.get("portfolio_state")
            if not portfolio_data:
                self.logger.warning("No portfolio data found, skipping rebalance")
                return
            
            portfolio = json.loads(portfolio_data)
            current_allocations = self.calculate_current_allocations(portfolio)
            
            # Calculate rebalancing actions
            rebalance_actions = self.calculate_rebalance_actions(
                current_allocations, 
                self.target_allocations
            )
            
            if rebalance_actions:
                # Publish rebalancing recommendations
                for action in rebalance_actions:
                    self.publish_rebalance_action(action)
                
                self.logger.info(f"📊 Generated {len(rebalance_actions)} rebalancing actions")
            else:
                self.logger.info("✅ Portfolio is already balanced")
                
        except Exception as e:
            self.logger.error(f"❌ Portfolio rebalancing error: {e}")
    
    def calculate_current_allocations(self, portfolio: Dict[str, Any]) -> Dict[str, float]:
        """Calculate current portfolio allocations"""
        total_value = portfolio.get("total_value", 0)
        positions = portfolio.get("positions", {})
        
        allocations = {}
        for symbol, position in positions.items():
            allocations[symbol] = position.get("value", 0) / total_value if total_value > 0 else 0
        
        return allocations
    
    def calculate_rebalance_actions(self, current: Dict[str, float], target: Dict[str, float]) -> List[Dict[str, Any]]:
        """Calculate required rebalancing actions"""
        actions = []
        tolerance = 0.05  # 5% tolerance
        
        for symbol in target:
            current_allocation = current.get(symbol, 0)
            target_allocation = target[symbol]
            difference = target_allocation - current_allocation
            
            if abs(difference) > tolerance:
                action_type = "BUY" if difference > 0 else "SELL"
                actions.append({
                    "type": "rebalance_action",
                    "action": action_type,
                    "symbol": symbol,
                    "current_allocation": current_allocation,
                    "target_allocation": target_allocation,
                    "difference": difference,
                    "priority": abs(difference)
                })
        
        # Sort by priority (largest differences first)
        actions.sort(key=lambda x: x["priority"], reverse=True)
        return actions
    
    def publish_rebalance_action(self, action: Dict[str, Any]):
        """Publish rebalancing action to Redis"""
        rebalance_event = {
            "type": "rebalance_recommendation",
            "timestamp": datetime.utcnow().isoformat(),
            **action
        }
        
        self.redis_client.publish("portfolio_actions", json.dumps(rebalance_event))

class SystemHealthMonitor:
    """Monitor system health and performance"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.logger = logging.getLogger("SystemHealthMonitor")
    
    async def check_system_health(self):
        """Perform comprehensive system health check"""
        try:
            self.logger.info("🏥 Starting system health check...")
            
            health_report = {
                "timestamp": datetime.utcnow().isoformat(),
                "components": {}
            }
            
            # Check Redis connectivity
            health_report["components"]["redis"] = await self.check_redis_health()
            
            # Check agent activity
            health_report["components"]["agents"] = await self.check_agent_activity()
            
            # Check data freshness
            health_report["components"]["data_freshness"] = await self.check_data_freshness()
            
            # Check system resources
            health_report["components"]["system_resources"] = await self.check_system_resources()
            
            # Calculate overall health score
            health_report["overall_health"] = self.calculate_health_score(health_report["components"])
            
            # Publish health report
            self.redis_client.publish("system_health", json.dumps(health_report))
            self.redis_client.set("last_health_check", json.dumps(health_report), ex=3600)  # 1 hour expiry
            
            self.logger.info(f"🏥 Health check completed - Overall score: {health_report['overall_health']:.2f}")
            
        except Exception as e:
            self.logger.error(f"❌ System health check error: {e}")
    
    async def check_redis_health(self) -> Dict[str, Any]:
        """Check Redis connectivity and performance"""
        try:
            start_time = time.time()
            self.redis_client.ping()
            response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "connected": True
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "connected": False
            }
    
    async def check_agent_activity(self) -> Dict[str, Any]:
        """Check if agents are processing events"""
        try:
            # Check for recent agent decisions
            decisions = self.redis_client.lrange("recent_agent_decisions", 0, 10)
            recent_decisions = len(decisions)
            
            return {
                "status": "healthy" if recent_decisions > 0 else "warning",
                "recent_decisions": recent_decisions,
                "agents_active": recent_decisions > 0
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_data_freshness(self) -> Dict[str, Any]:
        """Check if market data is fresh"""
        try:
            last_event = self.redis_client.get("last_market_event")
            if last_event:
                event_data = json.loads(last_event)
                event_time = datetime.fromisoformat(event_data["timestamp"].replace("Z", "+00:00"))
                age_minutes = (datetime.utcnow() - event_time.replace(tzinfo=None)).total_seconds() / 60
                
                return {
                    "status": "healthy" if age_minutes < 5 else "warning",
                    "last_update_minutes_ago": age_minutes,
                    "data_fresh": age_minutes < 5
                }
            else:
                return {
                    "status": "warning",
                    "last_update_minutes_ago": None,
                    "data_fresh": False
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "status": "healthy" if cpu_percent < 80 and memory.percent < 80 else "warning",
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "available_memory_gb": memory.available / (1024**3)
            }
        except ImportError:
            return {
                "status": "unknown",
                "error": "psutil not installed"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def calculate_health_score(self, components: Dict[str, Dict[str, Any]]) -> float:
        """Calculate overall health score (0-1)"""
        scores = []
        for component, health in components.items():
            if health["status"] == "healthy":
                scores.append(1.0)
            elif health["status"] == "warning":
                scores.append(0.6)
            else:
                scores.append(0.0)
        
        return sum(scores) / len(scores) if scores else 0.0

class MCPScheduler:
    """Main MCP scheduler that manages all automated tasks"""
    
    def __init__(self, redis_host="localhost", redis_port=6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
        self.logger = logging.getLogger("MCPScheduler")
        self.is_running = False
        
        # Initialize components
        self.market_collector = MarketDataCollector(self.redis_client)
        self.portfolio_rebalancer = PortfolioRebalancer(self.redis_client)
        self.health_monitor = SystemHealthMonitor(self.redis_client)
        
        # Setup schedules
        self.setup_schedules()
    
    def setup_schedules(self):
        """Setup all scheduled tasks"""
        # Market data collection - every 5 minutes during market hours
        schedule.every(5).minutes.do(
            lambda: asyncio.create_task(self.market_collector.collect_market_data())
        ).tag('market_data')
        
        # Portfolio rebalancing - daily at market open
        schedule.every().day.at("09:30").do(
            lambda: asyncio.create_task(self.portfolio_rebalancer.rebalance_portfolio())
        ).tag('portfolio')
        
                # System health check - every 15 minutes
        schedule.every(15).minutes.do(
            lambda: asyncio.create_task(self.health_monitor.check_system_health())
        ).tag('health_check')

        # Add more schedules as needed
        self.logger.info("📅 Schedules initialized")

    async def run_pending(self):
        """Run pending scheduled tasks"""
        while self.is_running:
            schedule.run_pending()
            await asyncio.sleep(1)

    async def start(self):
        """Start the scheduler"""
        self.is_running = True
        self.logger.info("🚀 Starting MCP Scheduler")
        
        # Start the schedule runner in a separate thread
        threading.Thread(target=lambda: asyncio.run(self.run_pending()), daemon=True).start()
        
        # Start any continuous processes
        await self.market_collector.restart_price_fetcher()

    async def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        self.logger.info("🛑 Stopping MCP Scheduler")
        
        # Cleanup any running processes
        subprocess.run(["pkill", "-f", "market_data_fetcher.py"], capture_output=True)

    async def add_task(self, task: MCPTask):
        """Add a new task to the scheduler"""
        try:
            # Serialize task and store in Redis
            task_data = {
                "id": task.id,
                "name": task.name,
                "command": task.command,
                "schedule_type": task.schedule_type,
                "schedule_config": task.schedule_config,
                "status": task.status.value,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "next_run": task.next_run.isoformat() if task.next_run else None
            }
            
            self.redis_client.hset("mcp_tasks", task.id, json.dumps(task_data))
            self.logger.info(f"➕ Added new task: {task.name} (ID: {task.id})")
            
            # Schedule the task based on its type
            if task.schedule_type == "interval":
                minutes = task.schedule_config.get("minutes", 5)
                schedule.every(minutes).minutes.do(
                    lambda: asyncio.create_task(self.execute_task(task))
                ).tag(task.id)
            elif task.schedule_type == "cron":
                time_str = task.schedule_config.get("time", "09:30")
                schedule.every().day.at(time_str).do(
                    lambda: asyncio.create_task(self.execute_task(task))
                ).tag(task.id)
            
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to add task: {e}")
            return False

    async def execute_task(self, task: MCPTask):
        """Execute a scheduled task"""
        try:
            # Update task status
            task.status = TaskStatus.RUNNING
            task.last_run = datetime.utcnow()
            await self.update_task_status(task)
            
            self.logger.info(f"⚡ Executing task: {task.name}")
            
            # Run the command
            result = subprocess.run(
                task.command.split(),
                capture_output=True,
                text=True,
                timeout=task.schedule_config.get("timeout", 300)
            )
            
            # Update task status based on result
            if result.returncode == 0:
                task.status = TaskStatus.COMPLETED
                task.output = result.stdout
                self.logger.info(f"✅ Task completed: {task.name}")
            else:
                task.status = TaskStatus.FAILED
                task.error = result.stderr
                self.logger.error(f"❌ Task failed: {task.name} - {result.stderr}")
            
            task.next_run = self.calculate_next_run(task)
            await self.update_task_status(task)
            
        except subprocess.TimeoutExpired:
            task.status = TaskStatus.FAILED
            task.error = "Task timed out"
            await self.update_task_status(task)
            self.logger.error(f"⏰ Task timed out: {task.name}")
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            await self.update_task_status(task)
            self.logger.error(f"❌ Task execution error: {task.name} - {e}")

    async def update_task_status(self, task: MCPTask):
        """Update task status in Redis"""
        task_data = {
            "id": task.id,
            "name": task.name,
            "status": task.status.value,
            "last_run": task.last_run.isoformat() if task.last_run else None,
            "next_run": task.next_run.isoformat() if task.next_run else None,
            "output": task.output,
            "error": task.error
        }
        
        self.redis_client.hset("mcp_tasks", task.id, json.dumps(task_data))
        self.redis_client.publish("task_updates", json.dumps(task_data))

    def calculate_next_run(self, task: MCPTask) -> datetime:
        """Calculate next run time for a task"""
        now = datetime.utcnow()
        
        if task.schedule_type == "interval":
            minutes = task.schedule_config.get("minutes", 5)
            return now + timedelta(minutes=minutes)
        elif task.schedule_type == "cron":
            time_str = task.schedule_config.get("time", "09:30")
            hour, minute = map(int, time_str.split(":"))
            
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            
            return next_run
        
        return now + timedelta(hours=1)  # Default fallback

    async def list_tasks(self) -> List[MCPTask]:
        """List all scheduled tasks"""
        tasks = []
        task_data = self.redis_client.hgetall("mcp_tasks")
        
        for task_json in task_data.values():
            task_dict = json.loads(task_json)
            tasks.append(MCPTask(
                id=task_dict["id"],
                name=task_dict["name"],
                command=task_dict["command"],
                schedule_type=task_dict["schedule_type"],
                schedule_config=task_dict["schedule_config"],
                status=TaskStatus(task_dict["status"]),
                last_run=datetime.fromisoformat(task_dict["last_run"]) if task_dict["last_run"] else None,
                next_run=datetime.fromisoformat(task_dict["next_run"]) if task_dict["next_run"] else None,
                output=task_dict.get("output", ""),
                error=task_dict.get("error", "")
            ))
        
        return tasks

async def main():
    """Main entry point for the MCP Scheduler"""
    scheduler = MCPScheduler()
    
    try:
        await scheduler.start()
        
        # Keep the main thread alive
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        await scheduler.stop()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        await scheduler.stop()

if __name__ == "__main__":
    asyncio.run(main())
