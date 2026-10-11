# WangAgent — 基于 DeepAgents 的可扩展 AI Agent 助手

<p align="center">
  <b>Python · DeepAgents · LangGraph · OpenSandbox · FastAPI · SQLite</b>
</p>

WangAgent 是一个面向复杂任务执行场景的 AI Agent 项目，基于 DeepAgents 构建 Agent 工作流，集成 OpenSandbox 隔离执行环境，并结合持久化记忆、模块化 Skills 和 Web 交互接口，探索从自然语言任务理解到工具执行、结果交付的完整 Agent 应用链路。

项目重点关注 Agent 的任务执行能力、上下文与记忆管理、执行环境隔离，以及可扩展的技能体系。

## 核心功能

### 1. Agent 工作流与任务执行
- 基于 DeepAgents 构建 Agent 核心执行流程。
- 接入大语言模型，支持自然语言任务交互。
- 结合工具调用与任务执行环境，探索复杂任务的自动化处理。

### 2. 分层记忆与持久化存储
- 使用 SQLite 持久化保存 Agent Checkpoint 和 Store 数据。
- 将会话状态持久化与长期记忆存储分离，便于管理不同类型的数据。
- 结合组织及用户标识管理运行上下文，为多用户场景下的记忆隔离提供基础。

### 3. OpenSandbox 隔离执行
- 集成 OpenSandbox，为 Agent 提供独立的任务执行环境。
- 通过 Docker 运行沙箱镜像，降低任务执行与宿主机环境之间的耦合。
- 设计沙箱连接、环境配置与生命周期管理流程。

### 4. Skills 技能扩展机制
- 通过模块化 Skills 扩展 Agent 的任务处理能力。
- 将技能说明、执行逻辑与 Agent 核心流程分离，便于后续增加新技能。
- 探索文档生成、文件处理等任务的自动化执行与交付。

### 5. Web 交互与服务集成
- 使用 FastAPI 提供后端服务接口。
- 支持浏览器端与 Agent 进行交互。
- 结合流式响应机制，探索对话过程的实时输出与任务结果反馈。

## 技术架构

```text
用户
 │
 ▼
Web 前端
 │
 ▼
FastAPI 服务层
 │
 ▼
DeepAgents / LangGraph
 │
 ├── LLM 接入层
 │
 ├── 记忆与持久化
 │    ├── SQLite Checkpoint
 │    └── SQLite Store
 │
 ├── Skills / Tools
 │
 └── OpenSandbox
      └── Docker 隔离执行环境
```

## 技术栈

| 技术 | 应用方向 |
|---|---|
| Python | 核心业务逻辑与服务端开发 |
| DeepAgents | Agent 创建与任务执行 |
| LangGraph | Agent 工作流及状态管理 |
| FastAPI | 后端 API 与 Web 服务 |
| OpenSandbox | 隔离式任务执行环境 |
| Docker | 沙箱容器运行 |
| SQLite | Checkpoint 与持久化存储 |
| 大语言模型 API | 自然语言理解与任务推理 |

## 项目结构

```text
WangAgent/
├── app/                 # Agent、模型及应用服务逻辑
├── build_harness/       # 运行环境与相关持久化数据
├── skills/              # 可扩展技能模块
├── static/              # Web 静态资源
├── tools/               # 工具及辅助逻辑
├── main.py              # 项目启动入口
├── pyproject.toml       # 项目依赖与配置
├── uv.lock              # 依赖锁定文件
├── sandbox.toml         # 沙箱服务配置
├── opensandbox.toml     # OpenSandbox 相关配置
└── README.md
```

## 本地部署

### 环境要求

- Python 版本以项目依赖配置为准
- Docker
- 可用的大语言模型 API
- OpenSandbox 服务端及对应沙箱镜像

### 启动步骤

1. 克隆项目：

   ```bash
   git clone <YOUR_GITHUB_REPOSITORY_URL>
   cd BuAgent
   ```

2. 安装项目依赖：

   根据 `pyproject.toml` 中的依赖管理方式安装。

3. 配置环境变量：

   根据项目实际配置创建 `.env` 文件，填写大语言模型 API 密钥、服务地址及 OpenSandbox 连接参数。

4. 启动 OpenSandbox 服务端，并确认沙箱镜像和连接配置正确。

5. 启动应用：

   ```bash
   python main.py
   ```

6. 根据终端输出访问 Web 页面。

## 项目实践与后续优化

当前项目围绕 Agent 工作流、记忆持久化、沙箱集成与技能扩展展开。后续可进一步完善：

- 沙箱文件与宿主机之间的安全文件传输及下载交付。
- 任务执行状态追踪、失败重试与异常恢复。
- 更细粒度的用户及组织数据隔离。
- Skills 自动发现、依赖管理与执行结果校验。
- 自动化测试、日志监控及部署流程。

## 安全说明

- 不要将 `.env`、API 密钥、个人访问令牌等敏感信息提交到公开仓库。
- 不要提交本地虚拟环境、运行日志及个人数据库文件。
- 对沙箱执行、文件访问和用户权限实施必要的安全限制。

## License

待补充。
