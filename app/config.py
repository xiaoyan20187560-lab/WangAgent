# ==================== 常量定义区 ====================
PATH_AGENTS_MEMORIES = "/memories/AGENTS.md"
PATH_USER_MEMORIES = "/memories/"
PATH_SKILLS = "/skills/"
#=================== model信息 ====================

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

STORE_DB_URI = r"E:\PYCHAMxuexilaji\BuAgent\build_harness\agent_store.db"
CHECKPOINT_DB_URI = r"E:\PYCHAMxuexilaji\BuAgent\build_harness\agent_checkpoint.db"

SANDBOX_IMAGE = os.getenv(
    "SANDBOX_IMAGE",
    "sandbox-registry.cn-zhangjiakou.cr.aliyuncs.com/opensandbox/code-interpreter:v1.0.1",
)
SANDBOX_IDLE_TIMEOUT = 10 * 60
SANDBOX_CLEANUP_INTERVAL = 60

PROJECT_ROOT = Path(__file__).parent.parent
LOCAL_SKILLS_DIR = PROJECT_ROOT / "skills"
PPT_SKILL_DIR = LOCAL_SKILLS_DIR / "wangding-pptx-generator"
PPT_CORE_DEPS = ["python-pptx"]
