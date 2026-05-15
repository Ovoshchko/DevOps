const fs = require('fs')
const path = require('path')

const [, , inputPath, outputPath] = process.argv

if (!inputPath || !outputPath) {
  console.error('Usage: node scripts/jest-to-sonar.js <jest-results.json> <sonar-test-execution.xml>')
  process.exit(1)
}

const escapeXml = (value) =>
  String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')

const toSonarPath = (absolutePath) => {
  const relativeToFrontend = path.relative(process.cwd(), absolutePath)
  return path.posix.join('frontend', relativeToFrontend.split(path.sep).join(path.posix.sep))
}

const results = JSON.parse(fs.readFileSync(inputPath, 'utf8'))
const files = results.testResults ?? []

const lines = ['<testExecutions version="1">']

for (const file of files) {
  lines.push(`  <file path="${escapeXml(toSonarPath(file.name))}">`)

  for (const assertion of file.assertionResults ?? []) {
    const duration = Math.max(0, assertion.duration ?? 0)
    const name = assertion.fullName || assertion.title || 'unnamed test'

    if (assertion.status === 'pending' || assertion.status === 'skipped') {
      lines.push(`    <testCase name="${escapeXml(name)}" duration="${duration}">`)
      lines.push('      <skipped message="Skipped"/>')
      lines.push('    </testCase>')
      continue
    }

    if (assertion.status === 'failed') {
      const message = assertion.failureMessages?.[0] ?? 'Test failed'
      const stacktrace = assertion.failureMessages?.join('\n\n') ?? message
      lines.push(`    <testCase name="${escapeXml(name)}" duration="${duration}">`)
      lines.push(`      <failure message="${escapeXml(message)}">${escapeXml(stacktrace)}</failure>`)
      lines.push('    </testCase>')
      continue
    }

    lines.push(`    <testCase name="${escapeXml(name)}" duration="${duration}"/>`)
  }

  lines.push('  </file>')
}

lines.push('</testExecutions>')

fs.mkdirSync(path.dirname(outputPath), { recursive: true })
fs.writeFileSync(outputPath, `${lines.join('\n')}\n`)
