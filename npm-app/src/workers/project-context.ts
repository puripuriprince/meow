import { parentPort as maybeParentPort } from 'worker_threads'

import { getAllFilePaths } from '@andji/common/project-file-tree'

import { initializeCheckpointFileManager } from '../checkpoints/file-manager'
import {
  getProjectFileContext,
  setProjectRoot,
  setChatIdFromExternal,
} from '../project-files'

if (maybeParentPort) {
  const parentPort = maybeParentPort

  parentPort.on('message', async ({ dir, chatId }) => {
    // Set the chat ID from main thread before any other operations
    if (chatId) {
      setChatIdFromExternal(chatId)
    }

    setProjectRoot(dir)
    const initFileContext = await getProjectFileContext(dir, {})
    if (!initFileContext) {
      throw new Error('Failed to initialize project file context')
    }

    const relativeFilepaths = getAllFilePaths(initFileContext.fileTree)
    await initializeCheckpointFileManager({
      projectDir: dir,
      relativeFilepaths,
    })

    parentPort.postMessage(initFileContext)
  })
}
