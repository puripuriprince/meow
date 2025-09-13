import * as fs from 'fs'
import * as path from 'path'

import { AGENT_TEMPLATES_DIR } from '@andji/common/old-constants'
import {
  filterCustomAgentFiles,
  extractAgentIdFromFileName,
} from '@andji/common/util/agent-file-utils'
import { green, yellow, cyan, magenta, bold, gray, red } from 'picocolors'

import {
  loadLocalAgents,
  getLoadedAgentNames,
  loadedAgents,
} from '../agents/load-agents'
import { getAllTsFiles } from '../agents/agent-utils'
import { CLI, getLocalAgentInfo } from '../cli'
import { createExampleAgentFiles } from './init-agents'
import { getProjectRoot } from '../project-files'
import {
  ENTER_ALT_BUFFER,
  EXIT_ALT_BUFFER,
  CLEAR_SCREEN,
  HIDE_CURSOR,
  SHOW_CURSOR,
} from '../utils/terminal'

let isInAgentsBuffer = false
let originalKeyHandlers: ((str: string, key: any) => void)[] = []
let selectedIndex = 0
let scrollOffset = 0
let allContentLines: string[] = []
let agentLinePositions: number[] = []
let agentList: Array<{
  id: string
  name: string
  description?: string
  isBuiltIn: boolean
  filePath?: string
  isCreateNew?: boolean
  isEditAgent?: boolean
  isSeparator?: boolean
  isPlaceholder?: boolean
  isSectionHeader?: boolean
}> = []

export function isInAgentsMode(): boolean {
  return isInAgentsBuffer
}

export async function enterAgentsBuffer(rl: any, onExit: () => void) {
  if (isInAgentsBuffer) {
    console.log(yellow('Already in agents mode!'))
    return
  }

  // Load local agents using the same logic as CLI startup
  await getLocalAgentInfo() // This updates the cache properly
  const localAgents = getLoadedAgentNames()

  // Build management actions section with header
  const actions: typeof agentList = [
    {
      id: '__header__',
      name: bold(cyan('Actions')),
      description: '',
      isBuiltIn: false,
      isSectionHeader: true,
    },
    {
      id: '__create_new__',
      name: '+ Create New Agent',
      description: 'Create a new custom agent template',
      isBuiltIn: false,
      isCreateNew: true,
    },
  ]

  // Build agent list starting with management actions
  agentList = [...actions]

  const agentsDir = path.join(getProjectRoot(), AGENT_TEMPLATES_DIR)

  const allAgentFiles = fs.existsSync(agentsDir) ? getAllTsFiles(agentsDir) : []

  const agentEntries = Object.entries(loadedAgents).map(([agentId, def]) => {
    // Find the file path for this agent by looking for files that match the agent ID
    const matchingPath = allAgentFiles.find((filePath) => {
      const relativePath = path.relative(agentsDir, filePath).replace('.ts', '')

      return (
        relativePath === agentId ||
        path.basename(filePath, '.ts').endsWith(agentId)
      )
    })

    let mtime = 0
    let filePath = ''
    if (matchingPath) {
      filePath = matchingPath
      try {
        mtime = fs.statSync(matchingPath).mtimeMs
      } catch {}
    }

    return {
      file: matchingPath
        ? path.relative(agentsDir, matchingPath)
        : `${agentId}.ts`,
      agentId,
      filePath,
      mtime,
      def,
    }
  })

  // Create agent description with file location
  const createAgentDescription = (entry: any) => {
    return entry.def?.description
      ? `${entry.def.description}`
      : `Custom user-defined agent`
  }

  const validAgents = agentEntries
    .filter((e) => e.def && e.def.id && e.def.model)
    .sort((a, b) => b.mtime - a.mtime)

  const now = Date.now()
  const sevenDaysMs = 7 * 24 * 60 * 60 * 1000
  const recentAgents = validAgents.filter((e) => now - e.mtime <= sevenDaysMs)
  const otherAgents = validAgents.filter((e) => now - e.mtime > sevenDaysMs)

  if (validAgents.length > 0) {
    if (recentAgents.length > 0) {
      agentList.push({
        id: '__recent_agents_header__',
        name: bold(cyan('Recently Updated')) + gray(' • last 7 days'),
        description: '',
        isBuiltIn: false,
        isSectionHeader: true,
      })

      for (const entry of recentAgents) {
        const agentName =
          localAgents[entry.agentId] || entry.def?.displayName || entry.agentId
        const description = createAgentDescription(entry)

        agentList.push({
          id: entry.agentId,
          name: agentName,
          description,
          isBuiltIn: false,
          filePath: entry.filePath,
        })
      }
    }

    if (otherAgents.length > 0) {
      agentList.push({
        id: '__agents_header__',
        name:
          bold(cyan('Custom Agents')) +
          gray(` • ${otherAgents.length} in ${AGENT_TEMPLATES_DIR}`),
        description: '',
        isBuiltIn: false,
        isSectionHeader: true,
      })

      for (const entry of otherAgents) {
        const agentName =
          localAgents[entry.agentId] || entry.def?.displayName || entry.agentId
        const description = createAgentDescription(entry)

        agentList.push({
          id: entry.agentId,
          name: agentName,
          description,
          isBuiltIn: false,
          filePath: entry.filePath,
        })
      }
    }
  } else {
    // No valid agents; show header + placeholder
    agentList.push({
      id: '__agents_header__',
      name:
        bold(cyan('Custom Agents')) +
        gray(` • ${allAgentFiles.length} in ${AGENT_TEMPLATES_DIR}`),
      description: '',
      isBuiltIn: false,
      isSectionHeader: true,
    })
    agentList.push({
      id: '__no_agents__',
      name: gray('No custom agents found'),
      description: 'Use "Create New Agent" above to get started',
      isBuiltIn: false,
      isPlaceholder: true,
    })
  }

  // Initialize selection to first selectable item
  selectedIndex = 0
  // Find first selectable item (skip section headers, separators, placeholders)
  while (
    selectedIndex < agentList.length &&
    (agentList[selectedIndex]?.isSectionHeader ||
      agentList[selectedIndex]?.isSeparator ||
      agentList[selectedIndex]?.isPlaceholder)
  ) {
    selectedIndex++
  }
  // If no selectable items found, default to 0
  if (selectedIndex >= agentList.length) {
    selectedIndex = 0
  }
  scrollOffset = 0

  // Enter alternate screen buffer
  process.stdout.write(ENTER_ALT_BUFFER)
  process.stdout.write(CLEAR_SCREEN)
  process.stdout.write(HIDE_CURSOR)

  isInAgentsBuffer = true

  // Build content and render
  buildAllContentLines()
  centerSelectedItem()
  renderAgentsList()

  // Set up key handler
  setupAgentsKeyHandler(rl, onExit)
}

export function exitAgentsBuffer(rl: any) {
  if (!isInAgentsBuffer) {
    return
  }

  // Reset state
  selectedIndex = 0
  scrollOffset = 0
  allContentLines = []
  agentLinePositions = []
  agentList = []

  // Restore all original key handlers
  if (originalKeyHandlers.length > 0) {
    process.stdin.removeAllListeners('keypress')
    originalKeyHandlers.forEach((handler) => {
      process.stdin.on('keypress', handler)
    })
    originalKeyHandlers = []
  }

  // Exit alternate screen buffer
  process.stdout.write(SHOW_CURSOR)
  process.stdout.write(EXIT_ALT_BUFFER)

  isInAgentsBuffer = false
}

function centerSelectedItem() {
  if (selectedIndex < 0 || selectedIndex >= agentLinePositions.length) {
    return
  }

  const terminalHeight = process.stdout.rows || 24
  const terminalWidth = process.stdout.columns || 80
  const headerHeight = getHeaderLines(terminalWidth).length
  const maxScrollableLines = terminalHeight - headerHeight - 2
  const selectedLineIndex = agentLinePositions[selectedIndex]
  const maxScrollOffset = Math.max(
    0,
    allContentLines.length - maxScrollableLines,
  )

  // Center item in the scrollable viewport
  const centerOffset = selectedLineIndex - Math.floor(maxScrollableLines / 2)
  scrollOffset = Math.max(0, Math.min(maxScrollOffset, centerOffset))
}

const getHeaderLines = (terminalWidth: number) => [
  // No header - sections will be labeled inline
]

function buildAllContentLines() {
  const terminalWidth = process.stdout.columns || 80
  const lines: string[] = []
  agentLinePositions = []

  if (agentList.length === 0) {
    lines.push(yellow('No agents found.'))
  } else {
    for (let i = 0; i < agentList.length; i++) {
      agentLinePositions.push(lines.length)
      const agent = agentList[i]
      const isSelected = i === selectedIndex

      // Handle section headers
      if (agent.isSectionHeader) {
        const cleanName = agent.name.replace(/\u001b\[[0-9;]*m/g, '')
        const cleanDescription = agent.description
          ? agent.description.replace(/\u001b\[[0-9;]*m/g, '')
          : ''
        const availableWidth = terminalWidth - 4 // Account for padding

        if (isSelected) {
          const headerWidth = Math.min(terminalWidth - 6, 60)
          lines.push(`  ${cyan('┌' + '─'.repeat(headerWidth + 2) + '┐')}`)

          // Right-aligned title with separator line
          const titlePadding = Math.max(0, headerWidth - cleanName.length - 4)
          const separatorLine = '─'.repeat(titlePadding)
          lines.push(
            `  ${cyan('│')} ${gray(separatorLine)}  ${agent.name} ${cyan('│')}`,
          )

          if (agent.description) {
            const descPadding = Math.max(
              0,
              headerWidth - cleanDescription.length,
            )
            lines.push(
              `  ${cyan('│')} ${agent.description}${' '.repeat(descPadding)} ${cyan('│')}`,
            )
          }
          lines.push(`  ${cyan('└' + '─'.repeat(headerWidth + 2) + '┘')}`)
        } else {
          // Right-aligned title with separator line for unselected
          const titlePadding = Math.max(
            0,
            availableWidth - cleanName.length - 4,
          )
          const separatorLine = gray('─'.repeat(titlePadding))
          lines.push(`  ${separatorLine}  ${agent.name}`)

          if (agent.description) {
            lines.push(`  ${agent.description}`)
          }
        }
        if (i < agentList.length - 1) {
          lines.push('') // Empty line after section header
        }
        continue
      }

      // Handle separator (keep for backwards compatibility)
      if (agent.isSeparator) {
        if (isSelected) {
          lines.push(`  ${cyan('┌' + '─'.repeat(52) + '┐')}`)
          lines.push(`  ${cyan('│')} ${gray(agent.name)} ${cyan('│')}`)
          lines.push(`  ${cyan('└' + '─'.repeat(52) + '┘')}`)
        } else {
          lines.push(`    ${gray(agent.name)}`)
        }
        if (i < agentList.length - 1) {
          lines.push('') // Empty line after separator
        }
        continue
      }

      // Handle placeholder
      if (agent.isPlaceholder) {
        if (isSelected) {
          const boxWidth = Math.min(terminalWidth - 6, 50)
          lines.push(`  ${cyan('┌' + '─'.repeat(boxWidth + 2) + '┐')}`)
          lines.push(
            `  ${cyan('│')} ${agent.name} ${' '.repeat(Math.max(0, boxWidth - agent.name.replace(/\u001b\[[0-9;]*m/g, '').length))} ${cyan('│')}`,
          )
          lines.push(
            `  ${cyan('│')} ${gray(agent.description || '')} ${' '.repeat(Math.max(0, boxWidth - (agent.description || '').length))} ${cyan('│')}`,
          )
          lines.push(`  ${cyan('└' + '─'.repeat(boxWidth + 2) + '┘')}`)
        } else {
          lines.push(`    ${agent.name}`)
          lines.push(`    ${gray(agent.description || '')}`)
        }
        if (i < agentList.length - 1) {
          lines.push('') // Empty line between items
        }
        continue
      }

      // Regular agent items
      const agentInfo =
        agent.isCreateNew || agent.isEditAgent
          ? `${agent.isCreateNew ? green(agent.name) : magenta(agent.name)}`
          : `${bold(agent.name)} ${gray(`(${agent.id})`)}`
      const description = agent.description || 'No description'
      const filePath = agent.filePath
        ? gray(`File: ${path.relative(getProjectRoot(), agent.filePath)}`)
        : ''

      const contentForBox = [
        agentInfo,
        gray(description),
        ...(filePath ? [filePath] : []),
      ]

      if (isSelected) {
        // Calculate box width based on content
        const maxContentWidth = Math.max(
          ...contentForBox.map(
            (line) => line.replace(/\u001b\[[0-9;]*m/g, '').length,
          ),
        )
        const boxWidth = Math.min(terminalWidth - 6, maxContentWidth)

        // Add top border
        lines.push(`  ${cyan('┌' + '─'.repeat(boxWidth + 2) + '┐')}`)

        // Add content lines with proper padding - keep same indentation as unselected
        contentForBox.forEach((line) => {
          const cleanLine = line.replace(/\u001b\[[0-9;]*m/g, '')
          const padding = ' '.repeat(Math.max(0, boxWidth - cleanLine.length))
          lines.push(`  ${cyan('│')} ${line}${padding} ${cyan('│')}`)
        })

        // Add bottom border
        lines.push(`  ${cyan('└' + '─'.repeat(boxWidth + 2) + '┘')}`)
      } else {
        // Non-selected items - use same base indentation as selected content
        lines.push(`    ${agentInfo}`) // 4 spaces to match selected content position
        lines.push(`    ${gray(description)}`)
        if (filePath) {
          lines.push(`    ${filePath}`)
        }
      }

      if (i < agentList.length - 1) {
        lines.push('') // Empty line between items
      }
    }
  }

  allContentLines = lines
}

function renderAgentsList() {
  // Build all content if not already built
  buildAllContentLines()

  // Clear screen and move cursor to top
  process.stdout.write(CLEAR_SCREEN)

  const terminalHeight = process.stdout.rows || 24
  const terminalWidth = process.stdout.columns || 80

  // Render fixed header
  const headerLines = getHeaderLines(terminalWidth)
  process.stdout.write(headerLines.join('\n'))
  process.stdout.write('\n')

  // Render scrollable content
  const maxScrollableLines = terminalHeight - headerLines.length - 2
  const visibleLines = allContentLines.slice(
    scrollOffset,
    scrollOffset + maxScrollableLines,
  )

  // Display scrollable content
  process.stdout.write(visibleLines.join('\n'))

  // Add padding to fill remaining space
  const remainingLines = maxScrollableLines - visibleLines.length
  if (remainingLines > 0) {
    process.stdout.write('\n'.repeat(remainingLines))
  }

  // Display status line at bottom
  const statusLine = `\n${gray(`Use ↑/↓/j/k to navigate, Enter to select, ESC or q to go back`)}`

  process.stdout.write(statusLine)
  process.stdout.write(HIDE_CURSOR)
}

function setupAgentsKeyHandler(rl: any, onExit: () => void) {
  // Store all original key handlers
  const listeners = process.stdin.listeners('keypress')
  originalKeyHandlers = listeners as ((str: string, key: any) => void)[]

  // Remove existing keypress listeners
  process.stdin.removeAllListeners('keypress')

  // Add our custom handler
  process.stdin.on('keypress', (str: string, key: any) => {
    // Support ESC or 'q' (no ctrl/meta) to go back
    if (
      (key && key.name === 'escape') ||
      (!key?.ctrl && !key?.meta && str === 'q')
    ) {
      exitAgentsBuffer(rl)
      onExit()
      return
    }

    // Handle Ctrl+C - exit to main screen
    if (key && key.ctrl && key.name === 'c') {
      exitAgentsBuffer(rl)
      onExit()
      return
    }

    // Handle Enter - add @<agent-name> to input field or create new agent
    if (key && key.name === 'return') {
      if (agentList.length > 0 && selectedIndex < agentList.length) {
        const selectedAgent = agentList[selectedIndex]

        // Skip separators, placeholders, and section headers
        if (
          selectedAgent.isSeparator ||
          selectedAgent.isPlaceholder ||
          selectedAgent.isSectionHeader
        ) {
          return
        }

        if (selectedAgent.isCreateNew) {
          exitAgentsBuffer(rl)
          startDirectAgentCreation(onExit)
        } else {
          exitAgentsBuffer(rl)
          // Instead of switching agents, add @<agent-name> to the input field
          const cliInstance = CLI.getInstance()
          const agentName = selectedAgent.name.replace(/\s*\(.*\)$/, '') // Remove any (id) suffix
          cliInstance.freshPrompt(`@${agentName} `)
        }
      }
      return
    }

    // Handle navigation - skip separators, placeholders, and section headers
    if (key && (key.name === 'up' || key.name === 'k')) {
      let newIndex = selectedIndex - 1
      while (
        newIndex >= 0 &&
        (agentList[newIndex]?.isSeparator ||
          agentList[newIndex]?.isPlaceholder ||
          agentList[newIndex]?.isSectionHeader)
      ) {
        newIndex--
      }
      if (newIndex >= 0) {
        selectedIndex = newIndex
        centerSelectedItem()
      }

      renderAgentsList()
      return
    }
    if (key && (key.name === 'down' || key.name === 'j')) {
      let newIndex = selectedIndex + 1
      while (
        newIndex < agentList.length &&
        (agentList[newIndex]?.isSeparator ||
          agentList[newIndex]?.isPlaceholder ||
          agentList[newIndex]?.isSectionHeader)
      ) {
        newIndex++
      }
      if (newIndex < agentList.length) {
        selectedIndex = newIndex
        centerSelectedItem()
        renderAgentsList()
      }
      return
    }

    if (key && key.name === 'pageup') {
      const newIndex = Math.max(0, selectedIndex - 5)
      if (newIndex !== selectedIndex) {
        selectedIndex = newIndex
        centerSelectedItem()
        renderAgentsList()
      }
      return
    }

    if (key && key.name === 'pagedown') {
      const newIndex = Math.min(agentList.length - 1, selectedIndex + 5)
      if (newIndex !== selectedIndex) {
        selectedIndex = newIndex
        centerSelectedItem()
        renderAgentsList()
      }
      return
    }

    if (key && key.name === 'home') {
      if (selectedIndex !== 0) {
        selectedIndex = 0
        centerSelectedItem()
        renderAgentsList()
      }
      return
    }

    if (key && key.name === 'end') {
      if (selectedIndex !== agentList.length - 1) {
        selectedIndex = agentList.length - 1
        centerSelectedItem()
        renderAgentsList()
      }
      return
    }
  })

  // Ensure raw mode for immediate key detection
  if (process.stdin.isTTY) {
    process.stdin.setRawMode(true)
  }
}

async function startDirectAgentCreation(onExit: () => void) {
  try {
    await createExampleAgentFiles()
    console.log(green('\n✅ Created example agent files in .agents directory!'))
    console.log(
      gray('Check out the files and edit them to create your custom agents.'),
    )
    console.log(
      gray('Run "andji --agent your-agent-id" to test your agents.'),
    )
  } catch (error) {
    console.error(red('Error creating example files:'), error)
  }

  onExit()
}

// Cleanup function
export function cleanupAgentsBuffer() {
  if (isInAgentsBuffer) {
    process.stdout.write(SHOW_CURSOR)
    process.stdout.write(EXIT_ALT_BUFFER)
    isInAgentsBuffer = false
  }

  // Restore normal terminal mode
  if (process.stdin.isTTY) {
    process.stdin.setRawMode(false)
  }
  // Register cleanup on process exit
  process.on('exit', cleanupAgentsBuffer)
  process.on('SIGINT', cleanupAgentsBuffer)
  process.on('SIGTERM', cleanupAgentsBuffer)
}
