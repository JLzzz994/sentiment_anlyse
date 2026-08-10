import asyncio

from engines.common.llm import LLMClient
from engines.common.reports import get_output_dir
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
        progress_callback: ProgressCallback | None = None # 进度列表为参数的 ProgressCallback = Callable[[ProgressUpdate], None]

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



async  def  main_test():
    await insight_agent_handler(
        role="insight",
        query="白海豚",
        task_id="1234",
        llm_client=LLMClient.from_role("insight"),
        output_dir=get_output_dir(task_id="1234",role="insight"),
        progress_callback=None
    )


if __name__ == '__main__':

    asyncio.run(main_test())