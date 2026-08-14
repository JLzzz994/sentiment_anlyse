from fastapi import APIRouter

from app.dependencies import SystemConfigServiceDep
from app.schemas.system_schema import ConfigResponse, ConfigUpdateRequest

system_router = APIRouter(prefix='/api/config', tags=['配置信息接口层'])
"""
指定响应模型，FastAPI 会自动：
① 校验返回数据是否符合该模型；
② 过滤掉未定义的字段；
③ 生成 OpenAPI 文档中的响应 schema
"""
@system_router.get(path="", response_model=ConfigResponse)
def get_config_info_endpoint(service:SystemConfigServiceDep):
    config_info_dict = service.get_config_info()
    return ConfigResponse(config=config_info_dict)

@system_router.post(path="")
def update_config_info_endpoint(
        config_request:ConfigUpdateRequest,
        service:SystemConfigServiceDep,
):
    service.update_config_info(config_request.root)