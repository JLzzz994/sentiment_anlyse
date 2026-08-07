from engines.common.llm import LLMClient


# 调用后拿到协程，await 后才拿到 str
async def insight_agent_handler(
        role:str,
        query:str,
        task_id:str,
        llm_client:LLMClient,
        output_dir:str
):
    """
    私域找数据
    """
    pass