from fastapi import APIRouter
from fastapi.responses import Response,FileResponse
from app.dependencies import ReportServiceDep
from app.schemas.report_schema import ReportStatusResponse, GenerateReportResponse, GenerateReportRequest

report_router = APIRouter(
    prefix='/api/report',
    tags=['报告路由'],
)


@report_router.get("/status", response_model=ReportStatusResponse, description='获取报告状态')
def get_report_status_endpoint(task_id: str, service: ReportServiceDep):
    input_status = service.get_report_status(task_id)
    return ReportStatusResponse(task_id=input_status.task_id, prepared=input_status.prepared,
                                found_files=input_status.found_files)


# response_model 1. 校验我给的返回值是否符合response_model后的类型, 2. 脱敏 3. FastAPIdocs中生成文档
@report_router.post('/generate', response_model=GenerateReportResponse, description='开始生成报告')
async def generate_report_endpoint(payload: GenerateReportRequest, service: ReportServiceDep):
    generation = service.request_report_generation(payload.task_id)
    return GenerateReportResponse(
        generation_id=generation.generation_id,
        task_id=generation.task_id
    )
# 前端预览报告接口
@report_router.get('/result/{generation_id}',description='获得报告生成结果')
def get_generate_result_endpoint(generation_id:str,service:ReportServiceDep):
    report_output = service.get_completed_report_output(generation_id)
    return Response(content=report_output.html_content,media_type='text/html')

@report_router.get('/download/{generation_id}/{file_type}',description='下载html或markdown格式报告')
def download_report_endpoint(generation_id:str,file_type:str,service:ReportServiceDep):
    file_info = service.get_download_file(generation_id,file_type)
    return FileResponse(file_info['file_path'],media_type=file_info['media_type'],filename=file_info['file_name'])