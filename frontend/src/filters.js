import str from '@/util/str'
import moment from '@/moment'

export function numFormat(num) {
  return str.numFormat(num)
}

export function formatBytes(num) {
  return str.bytesFormat(num)
}

export function substr(text, num) {
  return str.substr(text, num, '...')
}

export function dateFormat(date, format='LLL') {
  return moment(date).format(format);
}

