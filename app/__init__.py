from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from dotenv import load_dotenv

from .deep_agent import create_agent, _ensure_agents_memory
from .config import STORE_DB_URI, SANDBOX_IMAGE, CHECKPOINT_DB_URI
from .routes import router, set_globals
from .sandbox import init_sandbox_manager

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
#全局变量
_store: Any = None
_checkpointer: Any = None
_agent: Any = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 使用global声明来修改全局变量
    global _store, _checkpointer, _agent
    logger.info("Initializing database connections...")

    from contextlib import ExitStack
    from langgraph.checkpoint.sqlite import SqliteSaver
    from langgraph.store.sqlite import SqliteStore
    #上下文管理器，用于在应用程序生命周期内管理资源
    stack = ExitStack()
    try:
        _store = stack.enter_context(SqliteStore.from_conn_string(STORE_DB_URI))
        _checkpointer = stack.enter_context(SqliteSaver.from_conn_string(CHECKPOINT_DB_URI))
        # 建议添加：开启 WAL 模式，避免多请求并发写导致 database locked
        _store.conn.execute("PRAGMA journal_mode=WAL;")
        _store.conn.execute("PRAGMA busy_timeout=5000;")  # 5秒超时等待
        _store.setup()
        _checkpointer.setup()
        # 初始化沙箱管理器
        init_sandbox_manager(SANDBOX_IMAGE)

        _agent = create_agent(_checkpointer, _store)
        set_globals(_store, _checkpointer, _agent)

        # AGENTS.md 是全局配置：启动时确保唯一一份存在，并清理历史遗留的按用户副本
        try:
            _ensure_agents_memory(_store)
            #_remove_per_user_agents_memory(_store)
        except Exception as e:
            logger.warning(f"Failed to seed AGENTS.md at startup: {e}", exc_info=True)

        logger.info("Application started successfully.")
        yield
    except Exception as e:
        logger.error(f"Failed to initialize: {e}", exc_info=True)
        stack.close()
        from .sandbox import get_sandbox_manager
        mgr = get_sandbox_manager()
        if mgr:
            try:
                mgr.stop()
            except Exception:
                pass
        raise

    logger.info("Shutting down...")
    stack.close()
    from .sandbox import get_sandbox_manager
    mgr = get_sandbox_manager()
    if mgr:
        try:
            mgr.stop()
        except Exception as e:
            logger.error(f"Error stopping sandbox manager: {e}")


app = FastAPI(title="AI Chat Web", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    frontend_path = Path(__file__).parent.parent / "static" / "index.html"
    if frontend_path.exists():
        return FileResponse(str(frontend_path))
    return {"status": "ok", "message": "AI Chat API is running"}


@app.get("/@vite/client")
async def vite_client():
    return Response(content="", media_type="text/javascript")
