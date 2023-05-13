import { DateTime } from 'luxon'
import i18n from '@/i18n'

export default {
  nowUtime() {
    const date = new Date()
    const now = date.getTime()
    return  Math.floor(now / 1000)
  },

  utcDateStrFromJsDate(jsDate) {
    const dt = DateTime.fromJSDate(jsDate);
    return dt.toUTC().toFormat("yyyy-MM-dd'T'HH:mm:ss'Z'")
  },

  unixtimeFromStr(utcDateStr) {
    const dt = DateTime.fromISO(utcDateStr)
    return dt.toUnixInteger()
  },

  currentStr(format=DateTime.DATETIME_SHORT) {
    return DateTime.now().toFormat(format)
  },

  localeStrFromUtcDate(utcDateStr, format='') {
    if (!format) format = DateTime.DATETIME_SHORT
    const dt = DateTime.fromISO(utcDateStr).setLocale(i18n.locale)
    return dt.toLocaleString(format)
  },

  localeStrFromUnixtime(utime, format='') {
    if (!format) format = DateTime.DATETIME_SHORT
    const dt = DateTime.fromSeconds(utime).setLocale(i18n.locale)
    return dt.toLocaleString(format)
  },

  calcFromNow(value, unit='seconds', isFuture=true, format='') {
    if (!format) format = "yyyy-MM-dd'T'HH:mm:ss'Z'"
    let calcObj = {}
    calcObj[unit] = value
    if (isFuture) {
      return DateTime.utc().plus(calcObj).toFormat(format)
    } else {
      return DateTime.utc().minus(calcObj).toFormat(format)
    }
  },
}
