#!/usr/bin/env node

/**
 * Component Extraction Script
 *
 * Extracts inline components from dashboard.jsx into separate component files.
 *
 * Usage:
 *   node extract-component.js <component-name> <start-line> <end-line> [output-dir]
 *
 * Example:
 *   node extract-component.js ChatInterface 442 568
 *   node extract-component.js Header 303 339 src/components/layout
 */

const fs = require('fs')
const path = require('path')

// Parse command line arguments
const [,, componentName, startLine, endLine, outputDir = 'src/components'] = process.argv

// Validate arguments
if (!componentName || !startLine || !endLine) {
  console.error('Usage: node extract-component.js <component-name> <start-line> <end-line> [output-dir]')
  console.error('')
  console.error('Example:')
  console.error('  node extract-component.js ChatInterface 442 568')
  process.exit(1)
}

const start = parseInt(startLine, 10)
const end = parseInt(endLine, 10)

if (isNaN(start) || isNaN(end) || start > end) {
  console.error('Error: Invalid line numbers. Start must be less than end.')
  process.exit(1)
}

// Paths
const dashboardPath = path.join(process.cwd(), 'frontend', 'dashboard.jsx')
const outputPath = path.join(process.cwd(), 'frontend', outputDir, `${componentName}.jsx`)

// Read dashboard.jsx
if (!fs.existsSync(dashboardPath)) {
  console.error(`Error: Could not find dashboard.jsx at ${dashboardPath}`)
  process.exit(1)
}

const dashboardContent = fs.readFileSync(dashboardPath, 'utf-8')
const lines = dashboardContent.split('\n')

// Extract lines
const extractedLines = lines.slice(start - 1, end)
const extractedCode = extractedLines.join('\n')

// Generate component file content
const componentTemplate = `import React from 'react'
// TODO: Import any required icons from lucide-react
// import { Icon } from 'lucide-react'

/**
 * ${componentName} Component
 *
 * Extracted from dashboard.jsx lines ${start}-${end}
 *
 * TODO:
 * - Add prop types/TypeScript interface
 * - Import any missing dependencies
 * - Update hard-coded values to props
 * - Add tests
 */
export const ${componentName} = () => {
  // TODO: Move state from parent component if needed
  // TODO: Add props parameter

  return (
${extractedCode}
  )
}
`

// Create output directory if it doesn't exist
const outputDirPath = path.dirname(outputPath)
if (!fs.existsSync(outputDirPath)) {
  fs.mkdirSync(outputDirPath, { recursive: true })
  console.log(`Created directory: ${outputDirPath}`)
}

// Write component file
fs.writeFileSync(outputPath, componentTemplate)

console.log('✓ Component extracted successfully!')
console.log('')
console.log(`Component: ${componentName}`)
console.log(`Source: dashboard.jsx lines ${start}-${end}`)
console.log(`Output: ${outputPath}`)
console.log('')
console.log('Next steps:')
console.log('1. Review the generated component file')
console.log('2. Add prop types/interface')
console.log('3. Import required dependencies')
console.log('4. Update hard-coded values to props')
console.log('5. Import and use the component in dashboard.jsx')
console.log('6. Write tests')
console.log('')
console.log('Example usage in dashboard.jsx:')
console.log(`import { ${componentName} } from './${outputDir}/${componentName}'`)
console.log('')
console.log(`<${componentName} />`)
