<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue"
import { api } from "./api"

const sectionOrder = [
  ["platform_rule_changes", "平台规则变化与业务影响"],
  ["merchant_feedback", "商家反馈与集中诉求"],
  ["product_reputation", "商品口碑与问题趋势"],
  ["competitor_dynamics", "竞品动态与差异"],
  ["business_risk_opportunity", "经营风险与机会研判"]
]
const roleNames = { insight: "Insight 私域", media: "Media 公域", host: "Host 研判", report: "Report 报告" }

const examples = ref([])
const selectedExample = ref("")
const query = ref("")
const taskId = ref("")
const generationId = ref("")
const error = ref("")
const activeSection = ref(sectionOrder[0][0])
const roleFilter = ref("all")
const evidenceSections = ref([])
const hostSections = ref([])
const reportPrepared = ref(false)
const reportUrl = ref("")
const reportMessage = ref("等待研究完成")
const events = ref([])
const progress = ref({
  insight: 0, media: 0, host: 0, report: 0
})
let eventSource = null
let pollTimer = null

const activeEvidence = computed(() => {
  return evidenceSections.value
    .filter(s => s.section_key === activeSection.value)
    .filter(s => roleFilter.value === "all" || s.role === roleFilter.value)
    .flatMap(s => s.evidence.map(card => ({ ...card, role: s.role })))
})

const activeHost = computed(() =>
  hostSections.value.find(s => s.section_key === activeSection.value)
)

function selectExample(item) {
  selectedExample.value = item.id
  query.value = item.query
}

function channelLabel(channels) {
  const map = { db_call: "MySQL关键词", vector_call: "Milvus语义", web_call: "Web搜索" }
  return Object.keys(channels || {}).map(k => map[k] || k).join(" + ") || "未知通道"
}

function sourceLabel(card) {
  return card.source_name || card.platform || card.source_table || "未知来源"
}

async function loadExamples() {
  const data = await api.getExamples()
  examples.value = data.examples
  if (data.examples[0]) selectExample(data.examples[0])
}

function connectEvents() {
  if (eventSource) eventSource.close()
  eventSource = api.eventSource(taskId.value)
  eventSource.onmessage = event => {
    try {
      const payload = JSON.parse(event.data)
      events.value.unshift(payload)
      events.value = events.value.slice(0, 40)
      const d = payload.data || {}
      if (d.role && typeof d.progress_pct === "number") {
        progress.value[d.role] = d.progress_pct
      }
      if (payload.event === "role_result" && d.role) progress.value[d.role] = 100
    } catch (_) {}
  }
}

async function refreshVisualData() {
  if (!taskId.value) return
  try {
    const [evidence, judgements, report] = await Promise.all([
      api.getEvidence(taskId.value),
      api.getHostJudgements(taskId.value),
      api.getReportStatus(taskId.value)
    ])
    evidenceSections.value = evidence.sections || []
    hostSections.value = judgements.sections || []
    reportPrepared.value = report.prepared
    if (hostSections.value.length) progress.value.host = Math.round(hostSections.value.length / 5 * 100)
    reportMessage.value = report.prepared ? "研究输入已齐备，可生成综合报告" : "研究仍在进行"
  } catch (_) {}
}

function startPolling() {
  clearInterval(pollTimer)
  pollTimer = setInterval(refreshVisualData, 1800)
}

async function startResearch() {
  if (!query.value.trim()) return
  error.value = ""
  reportUrl.value = ""
  evidenceSections.value = []
  hostSections.value = []
  progress.value = { insight: 0, media: 0, host: 0, report: 0 }
  try {
    const data = await api.startResearch(query.value.trim())
    taskId.value = data.task_id
    connectEvents()
    startPolling()
    await refreshVisualData()
  } catch (e) {
    error.value = e.message
  }
}

async function generateReport() {
  if (!taskId.value || !reportPrepared.value) return
  error.value = ""
  try {
    const data = await api.generateReport(taskId.value)
    generationId.value = data.generation_id
    progress.value.report = 15
    reportMessage.value = "综合报告生成中"
    pollGeneration()
  } catch (e) {
    error.value = e.message
  }
}

async function pollGeneration() {
  if (!generationId.value) return
  try {
    const state = await api.getGenerationStatus(generationId.value)
    if (state.status === "completed") {
      progress.value.report = 100
      reportMessage.value = "报告生成完成"
      reportUrl.value = api.reportResultUrl(generationId.value)
      return
    }
    if (state.status === "error") {
      reportMessage.value = `报告生成失败：${state.error_message}`
      return
    }
    progress.value.report = 55
    setTimeout(pollGeneration, 1400)
  } catch (e) {
    error.value = e.message
  }
}

onMounted(loadExamples)
onBeforeUnmount(() => {
  if (eventSource) eventSource.close()
  clearInterval(pollTimer)
})
</script>

<template>
  <main class="shell">
    <header class="hero">
      <div>
        <p class="eyebrow">ECOMMERCE INTELLIGENCE</p>
        <h1>电商规则与口碑研判平台</h1>
        <p class="subtitle">Insight / Media / Host / Report 多 Agent 业务研究工作台</p>
      </div>
      <div v-if="taskId" class="task-chip">Task {{ taskId }}</div>
    </header>

    <section class="workspace">
      <aside class="left-panel">
        <div class="panel">
          <div class="panel-title"><span>01</span>业务 Case</div>
          <button
            v-for="item in examples"
            :key="item.id"
            class="case-card"
            :class="{ active: selectedExample === item.id }"
            @click="selectExample(item)"
          >
            <strong>{{ item.title }}</strong>
            <small>{{ item.scenario }}</small>
          </button>
        </div>

        <div class="panel">
          <div class="panel-title"><span>02</span>研究问题</div>
          <textarea v-model="query" rows="6" />
          <button class="primary" @click="startResearch">启动多 Agent 研判</button>
          <p v-if="error" class="error">{{ error }}</p>
        </div>

        <div class="panel">
          <div class="panel-title"><span>03</span>Agent 运行</div>
          <div v-for="role in ['insight','media','host','report']" :key="role" class="role-row">
            <div class="role-head">
              <span>{{ roleNames[role] }}</span>
              <b>{{ progress[role] }}%</b>
            </div>
            <div class="track"><i :style="{ width: progress[role] + '%' }" /></div>
          </div>
        </div>
      </aside>

      <section class="main-panel">
        <nav class="section-tabs">
          <button
            v-for="[key, title] in sectionOrder"
            :key="key"
            :class="{ active: activeSection === key }"
            @click="activeSection = key"
          >{{ title }}</button>
        </nav>

        <div class="two-col">
          <section class="panel evidence-panel">
            <div class="panel-heading">
              <div>
                <div class="panel-title"><span>04</span>证据卡片</div>
                <p>按章节查看私域与公域证据、来源及检索通道</p>
              </div>
              <div class="segmented">
                <button :class="{active:roleFilter==='all'}" @click="roleFilter='all'">全部</button>
                <button :class="{active:roleFilter==='insight'}" @click="roleFilter='insight'">Insight</button>
                <button :class="{active:roleFilter==='media'}" @click="roleFilter='media'">Media</button>
              </div>
            </div>

            <div v-if="!activeEvidence.length" class="empty">当前章节暂无已持久化证据</div>
            <article v-for="card in activeEvidence" :key="card.evidence_id + card.role" class="evidence-card">
              <div class="card-meta">
                <span class="role-badge">{{ roleNames[card.role] }}</span>
                <span>{{ sourceLabel(card) }}</span>
                <span>{{ card.source_table }}</span>
              </div>
              <h3 v-if="card.title">{{ card.title }}</h3>
              <p>{{ card.content }}</p>
              <div class="chips">
                <span class="channel">{{ channelLabel(card.retrieval_channels) }}</span>
                <span v-for="q in card.matched_queries" :key="q">命中：{{ q }}</span>
                <span v-if="card.rerank_score != null">排序分 {{ card.rerank_score.toFixed(3) }}</span>
                <span v-if="card.hotness_score">热度 {{ card.hotness_score }}</span>
              </div>
              <a v-if="card.url" :href="card.url" target="_blank" rel="noreferrer">查看原始来源 ↗</a>
            </article>
          </section>

          <section class="panel host-panel">
            <div class="panel-title"><span>05</span>Host 五章研判</div>
            <div v-if="!activeHost" class="empty">等待 Insight 与 Media 同章节结果齐备</div>
            <template v-else>
              <div class="judgement">{{ activeHost.host_judgement }}</div>
              <div class="signal-grid">
                <div>
                  <h4>风险信号</h4>
                  <ul><li v-for="x in activeHost.risk_signals" :key="x">{{ x }}</li></ul>
                </div>
                <div>
                  <h4>机会信号</h4>
                  <ul><li v-for="x in activeHost.opportunity_signals" :key="x">{{ x }}</li></ul>
                </div>
              </div>
              <details open>
                <summary>受影响对象</summary>
                <ul><li v-for="x in activeHost.affected_objects" :key="x">{{ x }}</li></ul>
              </details>
              <details open>
                <summary>建议动作</summary>
                <ul><li v-for="x in activeHost.recommended_actions" :key="x">{{ x }}</li></ul>
              </details>
              <details>
                <summary>一致观点 / 关键分歧</summary>
                <h4>一致观点</h4>
                <ul><li v-for="x in activeHost.aligned_points" :key="x">{{ x }}</li></ul>
                <h4>关键分歧</h4>
                <ul><li v-for="x in activeHost.conflicts" :key="x">{{ x }}</li></ul>
              </details>
              <details>
                <summary>证据情况与信息缺口</summary>
                <p>{{ activeHost.evidence_review }}</p>
              </details>
            </template>
          </section>
        </div>

        <section class="panel report-panel">
          <div class="report-head">
            <div>
              <div class="panel-title"><span>06</span>综合报告</div>
              <p>{{ reportMessage }}</p>
            </div>
            <button class="primary" :disabled="!reportPrepared" @click="generateReport">生成综合报告</button>
          </div>
          <iframe v-if="reportUrl" :src="reportUrl" title="综合研判报告" />
        </section>

        <section class="panel event-panel">
          <div class="panel-title"><span>TRACE</span>最近事件</div>
          <pre>{{ events.slice(0, 8).map(x => JSON.stringify(x)).join("\n") || "等待任务事件..." }}</pre>
        </section>
      </section>
    </section>
  </main>
</template>
