async function request(url, options = {}) {
  const response = await fetch(url, options)
  if (!response.ok) {
    let detail = `HTTP ${response.status}`
    try {
      const body = await response.json()
      detail = body.detail || detail
    } catch (_) {}
    throw new Error(detail)
  }
  return response.json()
}

export const api = {
  getExamples: () => request("/api/research/examples"),
  startResearch: (query) => request("/api/research", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query })
  }),
  getEvidence: (taskId) => request(`/api/research/evidence?task_id=${encodeURIComponent(taskId)}`),
  getHostJudgements: (taskId) => request(`/api/host/judgements?task_id=${encodeURIComponent(taskId)}`),
  getReportStatus: (taskId) => request(`/api/report/status?task_id=${encodeURIComponent(taskId)}`),
  generateReport: (taskId) => request("/api/report/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task_id: taskId })
  }),
  getGenerationStatus: (generationId) => request(
    `/api/report/generation/${encodeURIComponent(generationId)}/status`
  ),
  reportResultUrl: (generationId) => `/api/report/result/${encodeURIComponent(generationId)}`,
  eventSource: (taskId) => new EventSource(`/api/events/stream?task_id=${encodeURIComponent(taskId)}`)
}
