import str from '@/util/str'
import utilDate from '@/util/date'

export function numFormat(num) {
  return str.numFormat(num)
}

export function formatBytes(num) {
  return str.bytesFormat(num)
}

export function substr(text, num) {
  return str.substr(text, num, '...')
}

export function dateFormat(utcDateStr, format='') {
  return utilDate.localeStrFromUtcDate(utcDateStr, format)
}
