from fastapi import APIRouter
from fastapi.responses import HTMLResponse

demo_router = APIRouter(tags=["Demo"])


@demo_router.get("/demo", response_class=HTMLResponse, include_in_schema=False)
def ecommerce_demo_page() -> str:
    return """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>电商规则与口碑研判平台 Demo</title>
<style>
body{font-family:Arial,"PingFang SC","Microsoft YaHei",sans-serif;margin:0;background:#f6f7fb;color:#222}
header{padding:20px 28px;background:white;border-bottom:1px solid #e8e8ee;position:sticky;top:0}
h1{margin:0;font-size:22px}.sub{color:#666;margin-top:6px}
main{padding:24px;max-width:1400px;margin:auto}.grid{display:grid;grid-template-columns:1.05fr 1fr;gap:18px}
.card{background:white;border:1px solid #e6e7eb;border-radius:12px;padding:18px;margin-bottom:18px}
.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.case{border:1px solid #e4e5ea;border-radius:10px;padding:12px;cursor:pointer}
.case:hover{border-color:#999}.case.active{outline:2px solid #222}
button{border:0;border-radius:8px;padding:10px 14px;cursor:pointer;background:#222;color:white}
button.secondary{background:#eceef3;color:#222}.muted{color:#777;font-size:13px}
textarea{width:100%;min-height:105px;box-sizing:border-box;border:1px solid #dfe1e6;border-radius:8px;padding:10px}
.progress{height:8px;background:#eee;border-radius:4px;overflow:hidden}.bar{height:100%;background:#333;width:0%}
.role{display:grid;grid-template-columns:130px 1fr 48px;gap:10px;align-items:center;margin:10px 0}
#events,#discussion{max-height:360px;overflow:auto;background:#fafafa;border-radius:8px;padding:10px;font-size:13px;white-space:pre-wrap}
iframe{width:100%;height:650px;border:1px solid #ddd;border-radius:8px;background:white}
@media(max-width:900px){.grid,.cards{grid-template-columns:1fr}}
</style>
</head>
<body>
<header>
<h1>电商规则与口碑研判平台</h1>
<div class="sub">Insight / Media / Host / Report 多 Agent 业务演示</div>
</header>
<main>
<div class="grid">
<section>
<div class="card">
<h3>1. 选择业务 Case</h3>
<div id="cases" class="cards"></div>
</div>
<div class="card">
<h3>2. 发起研究</h3>
<textarea id="query"></textarea>
<div style="margin-top:12px;display:flex;gap:8px">
<button id="startBtn">启动多 Agent 研判</button>
<button class="secondary" id="reportBtn" disabled>生成综合报告</button>
</div>
<div class="muted" id="taskInfo" style="margin-top:10px"></div>
</div>
<div class="card">
<h3>3. Agent 实时进度</h3>
<div id="roles"></div>
<div id="events"></div>
</div>
</section>
<section>
<div class="card">
<h3>4. Host 研判讨论</h3>
<div id="discussion">尚未开始研究。</div>
</div>
<div class="card">
<h3>5. 最终报告</h3>
<div id="reportStatus" class="muted">等待研究完成。</div>
<div style="margin-top:10px"><iframe id="reportFrame"></iframe></div>
</div>
</section>
</div>
</main>
<script>
const state={taskId:null,generationId:null,eventSource:null,roles:{}};
const roleNames={insight:"Insight 私域研究",media:"Media 公域研究",host:"Host 研判",report:"Report 报告"};
function escapeHtml(s){return String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
function renderRoles(){
 const box=document.getElementById("roles"); box.innerHTML="";
 ["insight","media","host","report"].forEach(role=>{
  const v=state.roles[role]||{pct:0,status:"waiting"};
  box.innerHTML+=`<div class="role"><b>${roleNames[role]}</b><div class="progress"><div class="bar" style="width:${v.pct||0}%"></div></div><span>${v.pct||0}%</span></div>`;
 });
}
function logEvent(obj){
 const el=document.getElementById("events");
 el.textContent=(el.textContent?el.textContent+"\n":"")+JSON.stringify(obj,null,2);
 el.scrollTop=el.scrollHeight;
}
async function loadCases(){
 const r=await fetch("/api/research/examples"); const data=await r.json();
 const box=document.getElementById("cases");
 box.innerHTML=data.examples.map((x,i)=>`<div class="case" data-i="${i}"><b>${escapeHtml(x.title)}</b><div class="muted">${escapeHtml(x.scenario)}</div></div>`).join("");
 box.querySelectorAll(".case").forEach((el,i)=>el.onclick=()=>{
  box.querySelectorAll(".case").forEach(x=>x.classList.remove("active")); el.classList.add("active");
  document.getElementById("query").value=data.examples[i].query;
 });
 if(data.examples[0]){box.querySelector(".case").click()}
}
async function startResearch(){
 const query=document.getElementById("query").value.trim(); if(!query)return;
 state.roles={insight:{pct:0},media:{pct:0},host:{pct:0},report:{pct:0}}; renderRoles();
 document.getElementById("events").textContent="";
 document.getElementById("discussion").textContent="等待 Host 研判...";
 document.getElementById("reportFrame").src="about:blank";
 const r=await fetch("/api/research",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query})});
 const data=await r.json(); state.taskId=data.task_id;
 document.getElementById("taskInfo").textContent="task_id: "+state.taskId;
 document.getElementById("reportBtn").disabled=false;
 connectSSE(); pollHost(); pollReportPrepared();
}
function connectSSE(){
 if(state.eventSource)state.eventSource.close();
 const es=new EventSource("/api/events/stream?task_id="+encodeURIComponent(state.taskId)); state.eventSource=es;
 es.onmessage=e=>{
  try{
   const payload=JSON.parse(e.data); logEvent(payload);
   const d=payload.data||{}; const role=d.role;
   if(role){
    state.roles[role]=state.roles[role]||{};
    if(typeof d.progress_pct==="number")state.roles[role].pct=d.progress_pct;
    if(payload.event==="role_result")state.roles[role].pct=100;
    state.roles[role].status=d.status||payload.event; renderRoles();
   }
  }catch(err){logEvent({raw:e.data})}
 };
}
async function pollHost(){
 if(!state.taskId)return;
 try{
  const r=await fetch("/api/host/discussion?task_id="+encodeURIComponent(state.taskId));
  if(r.ok){
   const d=await r.json();
   document.getElementById("discussion").textContent=d.discussion_records.map(x=>`[${x.source}] ${x.dimension_key}\n${x.message_text}`).join("\n\n")||"等待 Host 研判...";
  }
 }catch(e){}
 setTimeout(pollHost,1800);
}
async function pollReportPrepared(){
 if(!state.taskId)return;
 try{
  const r=await fetch("/api/report/status?task_id="+encodeURIComponent(state.taskId)); const d=await r.json();
  document.getElementById("reportStatus").textContent=d.prepared?"研究输入已齐备，可生成综合报告。":"研究进行中，已完成: "+(d.found_files||[]).join(", ");
 }catch(e){}
 setTimeout(pollReportPrepared,2000);
}
async function generateReport(){
 if(!state.taskId)return;
 const r=await fetch("/api/report/generate",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({task_id:state.taskId})});
 if(!r.ok){document.getElementById("reportStatus").textContent="报告输入尚未就绪，请稍后再试。";return}
 const d=await r.json(); state.generationId=d.generation_id; state.roles.report={pct:10}; renderRoles(); pollGeneration();
}
async function pollGeneration(){
 if(!state.generationId)return;
 const r=await fetch("/api/report/generation/"+encodeURIComponent(state.generationId)+"/status");
 if(!r.ok)return;
 const d=await r.json();
 if(d.status==="completed"){
  state.roles.report={pct:100};renderRoles();
  document.getElementById("reportStatus").textContent="报告生成完成";
  document.getElementById("reportFrame").src="/api/report/result/"+encodeURIComponent(state.generationId);
 }else if(d.status==="error"){
  document.getElementById("reportStatus").textContent="报告生成失败: "+d.error_message;
 }else{
  state.roles.report={pct:55};renderRoles();
  document.getElementById("reportStatus").textContent="综合报告生成中...";
  setTimeout(pollGeneration,1500);
 }
}
document.getElementById("startBtn").onclick=startResearch;
document.getElementById("reportBtn").onclick=generateReport;
renderRoles();loadCases();
</script>
</body>
</html>"""
