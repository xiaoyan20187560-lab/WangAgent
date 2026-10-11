import logging
from typing import Any

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StoreBackend, StateBackend, FilesystemBackend
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.sqlite import SqliteStore
from .llm_factory import get_llm
from .config import LOCAL_SKILLS_DIR
from .context_type import MemoryContext
from .namespace_router import user_namespace
from .sandbox import _OrgScopedSandboxBackendProxy, get_sandbox_manager, _sandbox_available

logger = logging.getLogger(__name__)

# /memories/AGENTS.md 的初始内容（即系统提示词），首次使用时写入 PostgresStore
AGENTS_MEMORY = """你是一个智能助手，可以通过持续对话学习和记录用户的习惯与偏好。

## 关于用户习惯记录

在对话过程中，你应当主动观察用户的行为、言论和选择，识别以下类型的信息：

### 应该记录的内容：
- **编程语言与技术偏好**：用户常用的编程语言、框架、工具、代码风格等
- **工作习惯**：用户的工作流程、时间安排、常用工具、偏好的方法论等
- **沟通与输出偏好**：用户偏好的语言（中文/英文）、输出详细程度、格式要求、回复风格等
- **其他特征**：用户的特殊需求、注意事项、习惯、个人特点等

### 记录规则：
1. 使用 `edit_file` 工具将识别到的习惯追加到 `/memories/habits.md` 的对应分类下
2. 记录格式为：`- [具体习惯描述] (来源：YYYY-MM-DD 对话)`
3. 每次只记录新发现的习惯，不要重复已有内容
4. 如果用户明确要求"记住"某事，务必记录
5. 每个用户的习惯记录是相互隔离的，你只需关注当前对话用户

### 不应记录的内容：
- 临时性信息（如"我今天迟到了"、"帮我订个会议室"）
- 一次性任务请求
- 简单问答的答案
- 敏感信息（密码、密钥、身份证号等）
- 过期或无意义的闲聊

## PPT 制作能力（xiaobu-pptx-generator 技能）

**重要约束：绝不主动向用户提起、推销或询问是否需要制作 PPT。** 用户可能只是在闲聊、提问或做文件分析，不要主动提及 PPT，也不要主动给出 PPT 相关建议。只有当用户明确表达"做PPT/制作演示文稿/生成PPT/create PPT/做幻灯片/极简PPT/轻量化汇报PPT/导出pptx简报"等意图时，才按以下约定直接执行，无需额外确认：

1. 先用 `read_file` 读取 `/skills/xiaobu-pptx-generator/SKILL.md`（`limit=1000`）了解硬性约束与页面结构。
2. **两种使用方式**（任选其一，推荐方式一）：
   - **方式一（推荐）**：直接用 `execute` 运行沙箱中的脚本：
     ```
     python3 /skills/xiaobu-pptx-generator/generate_pptx.py \
       --topic "主题" \
       --points "要点1,要点2,要点3" \
       --page-num 5 \
       --output /workspace/light_presentation.pptx
     ```
     可选参数：`--data "10,25,30,15"`（极简柱状图数据）、`--json`（以JSON输出结果）
   - **方式二**：自行编写 Python 代码，参考 SKILL.md 中的 `generate_light_pptx` 函数代码，用 `write_file` 写入后再 `execute` 执行。
3. **关键约定**：
   - `SKILL_DIR` = `/skills/wangding-pptx-generator`
   - 读取技能文档用 `read_file`（路径以 `/skills/wangding-pptx-generator/` 开头）
   - 运行脚本用 `execute` 工具（当前组织沙箱，Linux 环境，`python3` 命令）
   - 核心依赖 `python-pptx` 已预装到沙箱
   - 输出文件保存到沙箱 `/workspace/` 目录下（绝对路径）
4. **生成 PPTX 后，必须提供可用的下载链接。**

   - 先确认生成脚本执行成功，并确认输出的 `.pptx` 文件确实存在。
   - 获取当前用户对应的 `org_id`，使用消息末尾【运行环境】中的组织 ID。
   - 下载接口为 `/sandbox/download`，如果 FastAPI 配置了 `/api` 路由前缀，则使用 `/api/sandbox/download`。
   - 将沙箱文件的绝对路径作为 `path` 参数，使用 URL 编码。
   - 下载链接必须指向当前运行的 FastAPI 服务，不能直接返回 `/workspace/xxx.pptx` 作为下载链接。
   - 返回 Markdown 格式的可点击链接，例如：`[点击下载 PPT](http://127.0.0.1:8000/sandbox/download?org_id=default-org&path=%2Fworkspace%2Flight_presentation.pptx)`。
   - 示例中的主机、端口、组织 ID 和文件名必须替换成当前运行环境的真实值，不得编造。
   - 如果无法确定实际可访问的下载地址，明确告知用户需要配置下载地址，不得声称已经提供下载链接。
5. 如遇到依赖缺失，可用 `execute` 运行 `python3 -m pip install python-pptx` 补装后重试。
6. 若沙箱刚创建、脚本尚未预装完成导致首次执行失败，等待几秒后重试即可。
7. **文件交付规则（必须执行）**

当用户要求生成 PPT、Word、Excel 等文件时：
- 必须先使用 execute 工具确认文件生成成功，并确认输出文件存在。
- 记录生成文件的沙箱绝对路径，例如 `/workspace/light_presentation.pptx`。
- 对 PPT 文件，必须返回 Markdown 格式的下载链接：
  `[下载 PPT 文件](/api/sandbox/download?org_id=实际组织ID&path=%2Fworkspace%2Flight_presentation.pptx)`
- 链接中的 `org_id` 必须使用当前对话的真实组织 ID；`path` 必须使用实际生成路径，并进行 URL 编码。
- 不得只回复沙箱路径，也不得声称文件已经下载到用户电脑。
- 如果文件生成失败或无法确认文件存在，明确告知用户失败原因。
"""


# AGENTS.md 是全局配置，与用户无关，统一存放在此命名空间（数据库仅一份）
AGENTS_NAMESPACE = ("global",)
AGENTS_KEY = "/AGENTS.md"


class _GlobalAgentsStore:
    """把 composite 剥离出的 "/" 归一化回 "/AGENTS.md" 的 Store 包装。

    CompositeBackend 对路由前缀与文件路径完全相等的路径（"/memories/AGENTS.md"）
    会把传入后端的 key 剥成 "/"，这里统一还原，保证全局只存一份 key="/AGENTS.md"。
    """

    def __init__(self, store: Any):
        self._store = store

    @staticmethod
    def _key(key: str) -> str:
        return AGENTS_KEY if key == "/" else key

    def get(self, namespace, key, *args, **kwargs):
        return self._store.get(namespace, self._key(key), *args, **kwargs)

    def aget(self, namespace, key, *args, **kwargs):
        return self._store.aget(namespace, self._key(key), *args, **kwargs)

    def put(self, namespace, key, value, *args, **kwargs):
        return self._store.put(namespace, self._key(key), value, *args, **kwargs)

    def aput(self, namespace, key, value, *args, **kwargs):
        return self._store.aput(namespace, self._key(key), value, *args, **kwargs)

    def delete(self, namespace, key, *args, **kwargs):
        return self._store.delete(namespace, self._key(key), *args, **kwargs)

    def adelete(self, namespace, key, *args, **kwargs):
        return self._store.adelete(namespace, self._key(key), *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._store, name)


def _ensure_agents_memory(store: SqliteStore):
    """确保全局 AGENTS.md（系统提示词配置）已存在且为当前版本，内容不一致时更新。"""
    current = {"content": AGENTS_MEMORY, "encoding": "utf-8"}
    existing = store.get(AGENTS_NAMESPACE, AGENTS_KEY)
    if existing:
        value = getattr(existing, "value", None) or {}
        stored_content = value.get("content") if isinstance(value, dict) else None
        if stored_content == AGENTS_MEMORY:
            return
        logger.info("Global /AGENTS.md differs from current version, updating.")
        store.put(AGENTS_NAMESPACE, AGENTS_KEY, current)
        return

    store.put(AGENTS_NAMESPACE, AGENTS_KEY, current)
    logger.info("Created global /AGENTS.md")


# def _remove_per_user_agents_memory(store: SqliteStore):
#     """清理历史遗留的按用户存放的 AGENTS.md 副本（只保留全局一份）。"""
#     try:
#         removed = 0
#         for ns in store.list_namespaces(limit=1000):
#             if len(ns) == 1 and ns != AGENTS_NAMESPACE:
#                 try:
#                     store.delete(ns, AGENTS_KEY)
#                     removed += 1
#                 except Exception:
#                     pass
#         if removed:
#             logger.info(f"Removed {removed} per-user AGENTS.md copy/copies.")
#     except Exception as e:
#         logger.warning(f"Failed to clean per-user AGENTS.md copies: {e}", exc_info=True)


def _ensure_user_habits(store: SqliteStore, user_id: str):
    HABITS_KEY = "/habits.md"
    NAMESPACE = (user_id,)

    existing = store.get(NAMESPACE, HABITS_KEY)
    if existing:
        return

    initial_content = """# 用户习惯记录

_此文件由 Agent 自动维护，持续记录用户的偏好、习惯和特点。_

## 编程语言与技术偏好
<!-- 用户使用的编程语言、框架、工具等偏好 -->

## 工作习惯
<!-- 用户的工作时间、工作流程、常用工具等 -->

## 沟通与输出偏好
<!-- 用户的语言风格、输出格式、详细程度等偏好 -->

## 其他特征
<!-- 用户的特殊习惯、需求、注意事项等 -->

---

_记录格式：_  
_## [类别名称]_  
_- [具体习惯描述] (来源：YYYY-MM-DD 对话)_
"""

    store.put(NAMESPACE, HABITS_KEY, {
        "content": initial_content,
        "encoding": "utf-8",
    })
    logger.info(f"Created /habits.md for user: {user_id}")


# 连接（或自动创建）本地数据库文件 agent_state.db
# checkpoint_conn = sqlite3.connect("../build_harness/agent_checkpoint.db", check_same_thread=False)
# store_conn = sqlite3.connect("../build_harness/agent_store.db", check_same_thread=False)
# store = SqliteStore(store_conn)
# checkpointer = SqliteSaver(checkpoint_conn)
# # 注意：若已有默认 Backend 实例（如 StateBackend），请在此初始化
# default_backend = StateBackend()

def create_agent(checkpointer: SqliteSaver, store: SqliteStore) -> Any:
    manager = get_sandbox_manager()
    if manager and manager.available:
        default_backend = _OrgScopedSandboxBackendProxy(manager)
        logger.info("Sandbox manager initialized (per-org container, 10-min idle recycle).")
    else:
        default_backend = StateBackend()
        logger.warning("Sandbox unavailable, running in degraded mode (no code execution).")
    model=get_llm()

    agent=create_deep_agent(
        model=model,
        context_schema=MemoryContext
        ,memory = ["./memories/AGENTS.md", "./memories/habits.md"],
        skills=['./buagent/skills/'],
        checkpointer=checkpointer,
        backend=CompositeBackend(
            default=default_backend,
            routes={
                # AGENTS.md 是全局配置：单独路由到全局命名空间（仅存一份），
                # habits.md 仍按用户命名空间隔离。
                "/memories/AGENTS.md": StoreBackend(
                    namespace=lambda _rt:AGENTS_NAMESPACE ,
                    store=_GlobalAgentsStore(store),
                ),
                "/memories/": StoreBackend(
                    namespace=lambda _rt:user_namespace,
                    store=store,
                ),
                "/skills/": FilesystemBackend(
                    root_dir=str(LOCAL_SKILLS_DIR),
                    virtual_mode=True,
                ),
            },
        )
    )
    return agent


