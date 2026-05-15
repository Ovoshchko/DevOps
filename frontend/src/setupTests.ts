import '@testing-library/jest-dom'
import { randomFillSync } from 'crypto'

if (!globalThis.crypto?.getRandomValues) {
  Object.defineProperty(globalThis, 'crypto', {
    configurable: true,
    value: {
      getRandomValues: <T extends ArrayBufferView>(array: T): T => randomFillSync(array as any) as T,
    },
  })
}

const defaultDateTimeFormatOptions: Intl.DateTimeFormatOptions = {
  year: 'numeric',
  month: 'numeric',
  day: 'numeric',
  hour: 'numeric',
  minute: '2-digit',
  second: '2-digit',
}

const defaultTimeFormatOptions: Intl.DateTimeFormatOptions = {
  hour: 'numeric',
  minute: '2-digit',
  second: '2-digit',
}

const formatInUtc = (value: Date, options: Intl.DateTimeFormatOptions) =>
  new Intl.DateTimeFormat('en-US', {
    timeZone: 'UTC',
    ...options,
  }).format(value)

Date.prototype.toLocaleString = function toLocaleString(
  locales?: string | string[],
  options?: Intl.DateTimeFormatOptions,
) {
  return formatInUtc(this, options ?? defaultDateTimeFormatOptions)
}

Date.prototype.toLocaleTimeString = function toLocaleTimeString(
  locales?: string | string[],
  options?: Intl.DateTimeFormatOptions,
) {
  return formatInUtc(this, options ?? defaultTimeFormatOptions)
}
