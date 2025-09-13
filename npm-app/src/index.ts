#!/usr/bin/env node

import { type CostMode } from '@andji/common/old-constants'
import { AnalyticsEvent } from '@andji/common/constants/analytics-events'
import { Command, Option } from 'commander'
import { red, yellow, green, bold } from 'picocolors'

import { displayLoadedAgents, loadLocalAgents } from './agents/load-agents'
import { CLI } from './cli'
import { cliArguments, cliOptions } from './cli-definitions'
import { handlePublish } from './cli-handlers/publish'
import { handleInitAgents } from './cli-handlers/init-agents'
import { npmAppVersion, backendUrl } from './config'
import { createTemplateProject } from './create-template-project'
import { printModeLog, setPrintMode } from './display/print-mode'
import { enableSquashNewlines } from './display/squash-newlines'
import { loadandjiConfig } from './json-config/parser'
import {
  getProjectRoot,
  getWorkingDirectory,
  initializeProjectRootAndWorkingDir,
  initProjectFileContextWithWorker,
} from './project-files'
import { rageDetectors } from './rage-detectors'
import { logAndHandleStartup } from './startup-process-handler'
import { recreateShell } from './terminal/run-command'
import { validateAgentDefinitionsIfAuthenticated } from './utils/agent-validation'
import { initAnalytics, trackEvent } from './utils/analytics'
import { logger } from './utils/logger'

import type { CliOptions } from './types'

async function andji({
  initialInput,
  git,
  costMode,
  runInitFlow,
  model,
  agent,
  params,
  print,
  cwd,
  trace,
}: CliOptions) {
  enableSquashNewlines()
  const workingDir = getWorkingDirectory()
  const projectRoot = getProjectRoot()
  await recreateShell(workingDir)

  // Kill all processes we failed to kill before
  const processCleanupPromise = logAndHandleStartup()

  initAnalytics()
  rageDetectors.startupTimeDetector.start()

  const initFileContextPromise = initProjectFileContextWithWorker(projectRoot)

  // Load agents and validate definitions
  const loadAndValidatePromise: Promise<void> = loadLocalAgents({
    verbose: true,
  }).then((agents) => {
    validateAgentDefinitionsIfAuthenticated(Object.values(agents))

    const andjiConfig = loadandjiConfig()
    if (!agent) {
      displayLoadedAgents(andjiConfig)
    }
  })

  const readyPromise = Promise.all([
    initFileContextPromise,
    processCleanupPromise,
    loadAndValidatePromise,
  ])

  // Initialize the CLI singleton
  CLI.initialize(readyPromise, {
    git,
    costMode,
    model,
    agent,
    params,
    print,
    trace,
  })

  const cli = CLI.getInstance()
  await cli.printInitialPrompt({ initialInput, runInitFlow })

  rageDetectors.startupTimeDetector.end()
}

if (require.main === module) {
  const program = new Command()

  program.name('andji').version(npmAppVersion || '0.0.0')

  // Add arguments from shared definitions
  cliArguments.forEach((arg) => {
    // For hidden arguments, just skip adding them to the help text
    if (!arg.hidden) {
      program.argument(arg.flags, arg.description)
    }
  })

  // Add options from shared definitions
  cliOptions.forEach((opt) => {
    const optionInstance = new Option(opt.flags, opt.description)
    if (opt.hidden) {
      optionInstance.hideHelp(true)
    }
    program.addOption(optionInstance)
  })

  program.addHelpText(
    'after',
    `
Examples:
  $ andji                                  # Start in current directory
  $ andji -p "tell me about the codebase"  # Print mode (non-interactive)
  $ andji --cwd my-project                 # Start in specific directory
  $ andji --trace                          # Enable subagent trace logging to .agents/traces/*.log
  $ andji --create nextjs my-app           # Create and scaffold a new Next.js project
  $ andji init-agents                      # Create example agent files in .agents directory
  $ andji publish my-agent                 # Publish agent template to store
  $ andji --agent file-picker "find relevant files for authentication"
  $ andji --agent reviewer --params '{"focus": "security"}' "review this code"

For all commands and options, run 'andji' and then type 'help'.
`,
  )

  program.parse()

  const options = program.opts()
  const args = program.args // Handle template creation

  // Initialize project root and working directory
  initializeProjectRootAndWorkingDir(options.cwd)

  if (options.create) {
    const template = options.create
    const projectDir = args[0] || '.'
    const projectName = args[1] || template
    createTemplateProject(template, projectDir, projectName)
    process.exit(0)
  }

  // Handle publish command
  if (args[0] === 'publish') {
    const agentNames = args.slice(1)
    await handlePublish(agentNames)
    process.exit(0)
  }

  // Handle init-agents command
  if (args[0] === 'init-agents') {
    await handleInitAgents()
    process.exit(0)
  }

  // Handle deprecated --pro flag
  if (options.pro) {
    console.error(
      red(
        'Warning: The --pro flag is deprecated. Please restart andji and use the --max option instead.',
      ),
    )
    logger.error(
      {
        errorMessage:
          'The --pro flag is deprecated. Please restart andji and use the --max option instead.',
      },
      'Deprecated --pro flag used',
    )
    process.exit(1)
  }

  // Determine cost mode
  let costMode: CostMode = 'normal'
  if (options.lite) {
    costMode = 'lite'
  } else if (options.max) {
    costMode = 'max'
  } else if (options.experimental) {
    costMode = 'experimental'
  } else if (options.ask) {
    costMode = 'ask'
  }

  // Handle git integration
  const git = options.git === 'stage' ? ('stage' as const) : undefined

  // Validate print mode requirements
  if (options.print) {
    const hasPrompt = args.length > 0
    const hasParams = options.params

    setPrintMode(true)
    trackEvent(AnalyticsEvent.PRINT_MODE, {
      args,
      options,
    })

    if (!hasPrompt && !hasParams) {
      printModeLog({
        type: 'error',
        message: 'Error: Print mode requires a prompt to be set',
      })
      process.exit(1)
    }
  }

  // Parse agent params if provided
  let parsedAgentParams: Record<string, any> | undefined
  if (options.params) {
    try {
      parsedAgentParams = JSON.parse(options.params)
    } catch (error) {
      console.error(red(`Error parsing --params JSON: ${error}`))
      process.exit(1)
    }
  }

  // Remove the first argument if it's the compiled binary path which bun weirdly injects (starts with /$bunfs)
  const filteredArgs = args[0]?.startsWith('/$bunfs') ? args.slice(1) : args

  // If first arg is a command like 'publish', don't treat it as initial input
  const isCommand = filteredArgs[0] === 'publish'
  const initialInput = isCommand ? '' : filteredArgs.join(' ')

  andji({
    initialInput,
    git,
    costMode,
    runInitFlow: options.init,
    model: options.model,
    agent: options.agent,
    params: parsedAgentParams,
    print: options.print,
    cwd: options.cwd,
    trace: options.trace,
  })
}
