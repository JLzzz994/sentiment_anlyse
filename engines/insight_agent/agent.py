

from engines.common.llm import LLMClient
from engines.common.research_graph_runtime import ResearchRunContext, ProgressCallback, handle_research_graph
from engines.contracts.agent_roles import RoleKey
from engines.insight_agent.graph import build_graph


# 调用后拿到协程，await 后才拿到 str
async def insight_agent_handler(
        role:RoleKey,
        query:str,
        task_id:str,
        llm_client:LLMClient,
        output_dir:str,
        progress_callback: ProgressCallback # 进度列表为参数的 ProgressCallback = Callable[[ProgressUpdate], None]

):
    """
    构建私域舆情智能体上下文与图,执行研究流程
    """
    ctx = ResearchRunContext(
        task_id = task_id,
        role=role,
        llm_client=llm_client,
        output_dir=output_dir,
        progress_callback=progress_callback,
    )
    await handle_research_graph(ctx,build_graph(ctx),query)
