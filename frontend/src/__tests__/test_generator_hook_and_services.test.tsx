import React from 'react'
import { act, renderHook } from '@testing-library/react'

import { DEFAULT_GENERATOR_CONFIG } from '../types/generator'
import { TrafficGeneratorService } from '../services/trafficGeneratorService'
import { useTrafficGenerator } from '../hooks/useTrafficGenerator'
import { monitoringApi } from '../services/monitoringApi'

jest.mock('../services/monitoringApi', () => ({
  monitoringApi: {
    ingest: jest.fn(),
  },
}))

describe('TrafficGeneratorService', () => {
  afterEach(() => {
    jest.restoreAllMocks()
    jest.clearAllMocks()
  })

  test('reports progress and completion across batches', async () => {
    const ingest = monitoringApi.ingest as jest.Mock
    ingest.mockResolvedValue({ accepted: 5 })

    const onProgress = jest.fn()
    const onComplete = jest.fn()
    const onError = jest.fn()
    const service = new TrafficGeneratorService()

    const runPromise = service.run(
      { ...DEFAULT_GENERATOR_CONFIG, batchSize: 5, intervalMs: 1, durationSeconds: 0.004 },
      { onProgress, onComplete, onError },
    )

    await runPromise

    expect(ingest).toHaveBeenCalledTimes(4)
    expect(onProgress).toHaveBeenCalledWith(expect.objectContaining({ sentBatches: 1, totalBatches: 4 }))
    expect(onComplete).toHaveBeenCalledWith(
      expect.objectContaining({ state: 'completed', sentBatches: 4, totalBatches: 4 }),
    )
    expect(onError).not.toHaveBeenCalled()
  })

  test('reports errors from ingest and stops processing', async () => {
    const ingest = monitoringApi.ingest as jest.Mock
    ingest.mockRejectedValue(new Error('ingest failed'))

    const onProgress = jest.fn()
    const onComplete = jest.fn()
    const onError = jest.fn()

    await new TrafficGeneratorService().run(
      { ...DEFAULT_GENERATOR_CONFIG, durationSeconds: 1, intervalMs: 1000 },
      { onProgress, onComplete, onError },
    )

    expect(onError).toHaveBeenCalledWith('ingest failed')
    expect(onProgress).not.toHaveBeenCalled()
    expect(onComplete).not.toHaveBeenCalled()
  })

  test('completes early when stopped before next batch', async () => {
    const ingest = monitoringApi.ingest as jest.Mock
    ingest.mockResolvedValue({ accepted: 1 })

    const onComplete = jest.fn()
    const service = new TrafficGeneratorService()
    const onProgress = jest.fn(() => {
      service.stop()
    })

    await service.run(
      { ...DEFAULT_GENERATOR_CONFIG, durationSeconds: 0.003, intervalMs: 1 },
      { onProgress, onComplete, onError: jest.fn() },
    )

    expect(onProgress).toHaveBeenCalled()
    expect(onComplete).toHaveBeenCalled()
  })
})

describe('useTrafficGenerator', () => {
  afterEach(() => {
    jest.restoreAllMocks()
  })

  test('runs generator lifecycle and calls onDataSent for progress and completion', async () => {
    const onDataSent = jest.fn()
    const runMock = jest
      .spyOn(TrafficGeneratorService.prototype, 'run')
      .mockImplementation(async (_config, handlers) => {
        handlers.onProgress({ sentBatches: 1, totalBatches: 2, acceptedPoints: 10 })
        handlers.onComplete({ sentBatches: 2, totalBatches: 2, completedAt: 'done' })
      })

    const { result } = renderHook(() => useTrafficGenerator(onDataSent))

    await act(async () => {
      await result.current.start()
    })

    expect(runMock).toHaveBeenCalled()
    expect(result.current.runState.state).toBe('completed')
    expect(result.current.runState.sentBatches).toBe(2)
    expect(onDataSent).toHaveBeenCalledTimes(2)
  })

  test('marks run as failed when service reports an error and reset returns to idle', async () => {
    jest.spyOn(TrafficGeneratorService.prototype, 'run').mockImplementation(async (_config, handlers) => {
      handlers.onError('generator failed')
    })

    const { result } = renderHook(() => useTrafficGenerator())

    await act(async () => {
      await result.current.start()
    })

    expect(result.current.runState.state).toBe('failed')
    expect(result.current.runState.lastError).toBe('generator failed')

    act(() => {
      result.current.reset()
    })

    expect(result.current.runState.state).toBe('idle')
  })

  test('stop delegates to active service and prevents duplicate start while running', async () => {
    let release!: () => void
    const pending = new Promise<void>((resolve) => {
      release = resolve
    })

    const stopMock = jest.spyOn(TrafficGeneratorService.prototype, 'stop').mockImplementation(() => {})
    const runMock = jest.spyOn(TrafficGeneratorService.prototype, 'run').mockImplementation(async () => pending)

    const { result } = renderHook(() => useTrafficGenerator())

    await act(async () => {
      void result.current.start()
      await Promise.resolve()
    })

    expect(result.current.canStart).toBe(false)

    await act(async () => {
      await result.current.start()
    })

    expect(runMock).toHaveBeenCalledTimes(1)

    act(() => {
      result.current.stop()
    })

    expect(stopMock).toHaveBeenCalled()
    expect(result.current.runState.state).toBe('completed')

    await act(async () => {
      release()
      await pending
    })
  })
})
