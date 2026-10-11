from pydantic import BaseModel, ConfigDict, Field

class MemoryContext(BaseModel):
    # 配置模型为不可变 (相当于 dataclass 的 frozen=True)
    model_config = ConfigDict(frozen=True)

    user_id: str = Field(default="local-user", description="用户ID")
    org_id: str = Field(default="default-org", description="组织ID")