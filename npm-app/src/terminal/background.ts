import assert from 'assert'
import { createWriteStream, mkdirSync } from 'fs'
import * as os from 'os'
import path, { dirname } from 'path'

import { stripColors } from '@andji/common/util/string'
import { green } from 'picocolors'

import {
  backgroundProcesses,
  spawnAndTrack,
} from '../background-process-manager'

import type { BackgroundProcessInfo } from '../background-process-manager'
import type { andjiToolOutput } from '@andji/common/tools/list'
import type { WriteStream } from 'fs'

export function runBackgroundCommand(
  options: {
    toolCallId: string
    command: string
    mode: 'user' | 'assistant' | 'manager'
    cwd: string
    stdoutFile?: string
    stderrFile?: string
  },
  resolveCommand: (value: andjiToolOutput<'run_terminal_command'>) => void,
): void {
  const { toolCallId, command, mode, cwd, stdoutFile, stderrFile } = options
  const isWindows = os.platform() === 'win32'
  const shell = isWindows ? 'cmd.exe' : 'bash'
  const shellArgs = isWindows ? ['/c'] : ['-c']

  if (mode === 'assistant') {
    console.log(green(`Running background process...\n> ${command}`))
  }

  try {
    const childProcess = spawnAndTrack(shell, [...shellArgs, command], {
      cwd,
      env: { ...process.env, FORCE_COLOR: '1' },
      // Ensure detached is always false to link child lifetime to parent
      detached: false,
      stdio: 'pipe',
    })

    // An error should have been thrown when we called `spawn`
    assert(
      childProcess.pid !== undefined,
      'Failed to spawn process: no PID assigned.',
    )

    const processId = childProcess.pid
    const processInfo: BackgroundProcessInfo = {
      pid: processId,
      toolCallId,
      command,
      process: childProcess,
      stdoutBuffer: [],
      stderrBuffer: [],
      status: 'running',
      startTime: Date.now(),
      endTime: null,
      lastReportedStdoutLength: 0,
      lastReportedStderrLength: 0,
      lastReportedStatus: null,
      stdoutFile,
      stderrFile,
    }
    backgroundProcesses.set(processId, processInfo)

    // Set up file streams if paths are provided
    let stdoutStream: WriteStream | undefined
    let stderrStream: WriteStream | undefined

    if (stdoutFile) {
      const stdoutAbs = path.isAbsolute(stdoutFile)
        ? stdoutFile
        : path.join(cwd, stdoutFile)
      mkdirSync(dirname(stdoutAbs), { recursive: true })
      stdoutStream = createWriteStream(stdoutAbs)
    }

    const realStderrFile = stderrFile || stdoutFile
    if (realStderrFile) {
      const stderrAbs = path.isAbsolute(realStderrFile)
        ? realStderrFile
        : path.join(cwd, realStderrFile)
      mkdirSync(dirname(stderrAbs), { recursive: true })
      stderrStream = createWriteStream(stderrAbs)
    }

    childProcess.stdout.on('data', (data: Buffer) => {
      const output = stripColors(data.toString())
      processInfo.stdoutBuffer.push(output)

      // Write to file if stream exists
      if (stdoutStream) {
        stdoutStream.write(output)
      }
    })

    childProcess.stderr.on('data', (data: Buffer) => {
      const output = stripColors(data.toString())
      processInfo.stderrBuffer.push(output)

      // Write to file if stream exists
      if (stderrStream) {
        stderrStream.write(output)
      }
    })

    childProcess.on('error', (error) => {
      processInfo.status = 'error'
      processInfo.stderrBuffer.push(
        `\nError spawning command: ${error.message}`,
      )
      processInfo.endTime = Date.now()

      // Close file streams
      stdoutStream?.end()
      stderrStream?.end()
    })

    let exitCode = null

    childProcess.on('close', (code) => {
      exitCode = code
      processInfo.status = code === 0 ? 'completed' : 'error'
      processInfo.endTime = Date.now()

      // Close file streams
      stdoutStream?.end()
      stderrStream?.end()
    })

    // Unreference the process so the parent can exit independently IF the child is the only thing keeping it alive.
    childProcess.unref()

    resolveCommand([
      {
        type: 'json',
        value: {
          command,
          processId,
          backgroundProcessStatus: processInfo.status,
        },
      },
    ])
  } catch (error: any) {
    resolveCommand([
      {
        type: 'json',
        value: {
          command,
          errorMessage: error.message,
        },
      },
    ])
  }
}
