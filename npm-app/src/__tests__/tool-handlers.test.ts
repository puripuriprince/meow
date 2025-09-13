import fs from 'fs'
import path from 'path'

import {
  clearMockedModules,
  mockModule,
} from '@andji/common/testing/mock-modules'
import {
  afterAll,
  afterEach,
  beforeAll,
  beforeEach,
  describe,
  expect,
  mock,
  test,
} from 'bun:test'

import { handleCodeSearch } from '../tool-handlers'

describe('handleCodeSearch', () => {
  const testDataDir = path.resolve(__dirname, 'data')
  // Mock getProjectRoot to point to npm-app directory
  const mockGetProjectRoot = mock(() => {
    const projectRoot = path.resolve(__dirname, '../../')
    return projectRoot
  })

  beforeAll(() => {
    mockModule('@andji/npm-app/project-files', () => ({
      getProjectRoot: mockGetProjectRoot,
    }))
  })

  beforeEach(async () => {
    const projectRoot = path.resolve(__dirname, '../../')
    mockGetProjectRoot.mockReturnValue(projectRoot)
    console.log('Setting mock project root to:', projectRoot)
    console.log('testDataDir', testDataDir)

    // Create test data directory and files
    await fs.promises.mkdir(testDataDir, { recursive: true })

    // Create test files with specific content
    await fs.promises.writeFile(
      path.join(testDataDir, 'test-content.js'),
      `// Test file for code search
export function testFunction() {
  console.log('UNIQUE_SEARCH_STRING_12345');
  return 'findme_xyz789';
}

export const FINDME_XYZ789 = 'uppercase version';
`,
    )

    await fs.promises.writeFile(
      path.join(testDataDir, 'another-file.ts'),
      `// Another test file
export interface TestInterface {
  UNIQUE_SEARCH_STRING_12345: string;
}
`,
    )
  })

  afterEach(async () => {
    // Clean up test data directory
    try {
      await fs.promises.rm(testDataDir, { recursive: true, force: true })
    } catch (error) {
      // Ignore cleanup errors
    }
  })

  afterAll(() => {
    clearMockedModules()
  })

  test('calls getProjectRoot and handles execution', async () => {
    const parameters = {
      pattern: 'testFunction',
      cwd: '__tests__/data',
    }

    await handleCodeSearch(parameters, 'test-id')

    expect(mockGetProjectRoot).toHaveBeenCalled()
  })

  test('handles basic search without cwd', async () => {
    const parameters = {
      pattern: 'export',
    }

    const result = await handleCodeSearch(parameters, 'test-id')

    expect(result[0].value).toContainKey('message')
  })

  test('finds specific content in test file', async () => {
    const parameters = {
      pattern: 'UNIQUE_SEARCH_STRING_12345',
      cwd: 'src/__tests__/data',
    }

    const result = await handleCodeSearch(parameters, 'test-id')

    expect(mockGetProjectRoot).toHaveBeenCalled()
    expect((result[0].value as any).stdout).toContain(
      'UNIQUE_SEARCH_STRING_12345',
    )
    expect((result[0].value as any).stdout).toContain('test-content.js')
  })

  test('searches with case-insensitive flag', async () => {
    const parameters = {
      pattern: 'findme_xyz789',
      flags: '-i',
      cwd: 'src/__tests__/data',
    }

    const result = await handleCodeSearch(parameters, 'test-id')

    expect((result[0].value as any).stdout).toContain('findme_xyz789')
  })
})
