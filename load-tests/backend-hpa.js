import http from 'k6/http'
import { check, sleep } from 'k6'

export const options = {
  vus: Number(__ENV.VUS || 10),
  duration: __ENV.DURATION || '2m',
  thresholds: {
    http_req_failed: ['rate<0.2'],
    http_req_duration: ['p(95)<3000'],
  },
}

const baseUrl = (__ENV.BASE_URL || 'http://localhost:3000').replace(/\/$/, '')
const initiatedBy = __ENV.INITIATED_BY || 'k6'

export function setup() {
  const detectorsResponse = http.get(`${baseUrl}/api/detectors`)
  const ok = check(detectorsResponse, {
    'detectors status is 200': (r) => r.status === 200,
  })

  if (!ok) {
    throw new Error(
      `Failed to load detectors: status=${detectorsResponse.status} error="${detectorsResponse.error || ''}" body="${detectorsResponse.body || ''}"`
    )
  }

  const detectors = detectorsResponse.json()
  if (!Array.isArray(detectors) || detectors.length === 0) {
    throw new Error('No detectors available for load test')
  }

  const activeDetector = detectors.find((detector) => detector.status === 'active') || detectors[0]
  return { detectorId: activeDetector.id }
}

export default function (data) {
  const windowEnd = new Date()
  const windowStart = new Date(windowEnd.getTime() - 60 * 1000)

  const payload = JSON.stringify({
    detector_config_id: data.detectorId,
    window_start: windowStart.toISOString(),
    window_end: windowEnd.toISOString(),
    initiated_by: initiatedBy,
  })

  const response = http.post(`${baseUrl}/api/detections/run`, payload, {
    headers: {
      'Content-Type': 'application/json',
    },
  })

  check(response, {
    'detection run status is 201': (r) => r.status === 201,
  })

  sleep(Number(__ENV.SLEEP || 0.5))
}
