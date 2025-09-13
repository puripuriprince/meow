import { Writable } from 'stream'

import * as projectFileTree from '@andji/common/project-file-tree'
import { getToolCallString } from '@andji/common/tools/utils'
import {
  afterEach,
  beforeEach,
  describe,
  expect,
  mock,
  spyOn,
  test,
} from 'bun:test'
import stripAnsi from 'strip-ansi'

import * as projectFiles from '../../project-files'
import { toolRenderers } from '../../utils/tool-renderers'
import { createXMLStreamParser } from '../xml-stream-parser'

describe('Tool renderers with XML parser', () => {
  beforeEach(() => {
    spyOn(projectFileTree, 'isFileIgnored').mockImplementation(() => false)
    spyOn(projectFiles, 'getProjectRoot').mockImplementation(() => '/test/path')
  })

  afterEach(() => {
    mock.restore()
  })

  // Helper function to process XML through parser and get output
  async function processXML(xml: string): Promise<string> {
    let result = ''
    const processor = createXMLStreamParser(toolRenderers)

    const writable = new Writable({
      write(chunk, encoding, callback) {
        result += chunk.toString()
        callback()
      },
    })

    processor.pipe(writable)
    processor.write(xml)
    processor.end()

    // Wait for stream to finish
    await new Promise<void>((resolve) => {
      writable.on('finish', resolve)
    })

    return result
  }

  test('formats write_file tool call', async () => {
    const xml = getToolCallString('write_file', {
      path: 'test.ts',
      content: 'console.log("test");\n',
      instructions: 'add a console.log statement',
    })
    const output = await processXML(xml)
    const stripped = stripAnsi(output)
    expect(stripped).toBe(
      '\n\n[Write File]\nEditing file at test.ts...\nadd a console.log statement\n\n',
    )
  })

  test('formats read_files tool call', async () => {
    const xml = getToolCallString('read_files', {
      paths: ['file1.ts', 'file2.ts'],
    })
    const output = await processXML(xml)
    const stripped = stripAnsi(output)
    expect(stripped).toBe('\n\n[Read Files]\nfile1.ts\nfile2.ts\n\n')
  })

  test('formats set_output tool call', async () => {
    const xml = getToolCallString('set_output', {
      message: 'Task completed successfully',
      result: { status: 'success', count: 42 },
    })
    const output = await processXML(xml)
    const stripped = stripAnsi(output)
    expect(stripped).toContain('[Set Output]')
    expect(stripped).toContain('Task completed successfully')
    // Should NOT contain the result parameter - only message should be shown
    expect(stripped).not.toContain('{"status":"success","count":42}')
    expect(stripped).not.toContain('result')
  })
})
