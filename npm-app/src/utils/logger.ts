import { mkdirSync } from 'fs'
import path, { dirname } from 'path'
import { format as stringFormat } from 'util'

import { AnalyticsEvent } from '@andji/common/constants/analytics-events'
import { pino } from 'pino'

import { getCurrentChatDir, getProjectRoot } from '../project-files'
import { flushAnalytics, logError, trackEvent } from './analytics'

export interface LoggerContext {
  userId?: string
  userEmail?: string
  clientSessionId?: string
  fingerprintId?: string
  clientRequestId?: string
  [key: string]: any // Allow for future extensions
}

export const loggerContext: LoggerContext = {}

const analyticsBuffer: { analyticsEventId: AnalyticsEvent; toTrack: any }[] = []

let logPath: string | undefined = undefined
let pinoLogger: any = undefined

const loggingLevels = ['info', 'debug', 'warn', 'error', 'fatal'] as const
type LogLevel = (typeof loggingLevels)[number]

function setLogPath(p: string): void {
  if (p === logPath) return // nothing to do

  logPath = p
  mkdirSync(dirname(p), { recursive: true })

  // ──────────────────────────────────────────────────────────────
  //  pino.destination(..) → SonicBoom stream, no worker thread
  // ──────────────────────────────────────────────────────────────
  const fileStream = pino.destination({
    dest: p, // absolute or relative file path
    mkdir: true, // create parent dirs if they don’t exist
    sync: false, // set true if you *must* block on every write
  })

  pinoLogger = pino(
    {
      level: 'debug',
      formatters: {
        level: (label) => ({ level: label.toUpperCase() }),
      },
      timestamp: () => `,"timestamp":"${new Date().toISOString()}"`,
    },
    fileStream, // <-- no worker thread involved
  )
}

function sendAnalyticsAndLog(
  level: LogLevel,
  data: any,
  msg?: string,
  ...args: any[]
): void {
  if (
    process.env.andji_GITHUB_ACTIONS !== 'true' &&
    process.env.NEXT_PUBLIC_CB_ENVIRONMENT !== 'test'
  ) {
    const projectRoot = getProjectRoot() || process.cwd()

    const logTarget =
      process.env.NEXT_PUBLIC_CB_ENVIRONMENT === 'dev'
        ? path.join(projectRoot, 'debug', 'npm-app.log')
        : (() => {
            try {
              return path.join(getCurrentChatDir(), 'log.jsonl')
            } catch {
              return path.join(projectRoot, 'debug', 'npm-app.log')
            }
          })()

    setLogPath(logTarget)
  }

  const toTrack = {
    data,
    level,
    loggerContext,
    msg: stringFormat(msg, ...args),
  }

  logAsErrorIfNeeded(toTrack)

  logOrStore: if (
    process.env.NEXT_PUBLIC_CB_ENVIRONMENT !== 'dev' &&
    Object.values(AnalyticsEvent).includes(data.eventId)
  ) {
    const analyticsEventId = data.eventId as AnalyticsEvent
    // Not accurate for anonymous users
    if (!loggerContext.userId) {
      analyticsBuffer.push({ analyticsEventId, toTrack })
      break logOrStore
    }

    for (const item of analyticsBuffer) {
      trackEvent(item.analyticsEventId, item.toTrack)
    }
    analyticsBuffer.length = 0
    trackEvent(analyticsEventId, toTrack)
  }

  if (pinoLogger !== undefined) {
    pinoLogger[level]({ ...loggerContext, data }, msg, ...args)
  }
}

function logAsErrorIfNeeded(toTrack: {
  data: any
  level: LogLevel
  loggerContext: LoggerContext
  msg: string
}) {
  if (toTrack.level === 'error' || toTrack.level === 'fatal') {
    logError(
      new Error(toTrack.msg),
      toTrack.loggerContext.userId ?? 'unknown',
      { ...toTrack.data, context: toTrack.loggerContext },
    )
    flushAnalytics()
  }
}

/**
 * Wrapper around Pino logger.
 *
 * To also send to Posthog, set data.eventId to type AnalyticsEvent
 *
 * e.g. logger.info({eventId: AnalyticsEvent.SOME_EVENT, field: value}, 'some message')
 */
export const logger: Record<LogLevel, pino.LogFn> = Object.fromEntries(
  loggingLevels.map((level) => {
    return [
      level,
      (data: any, msg?: string, ...args: any[]) =>
        sendAnalyticsAndLog(level, data, msg, ...args),
    ]
  }),
) as Record<LogLevel, pino.LogFn>
