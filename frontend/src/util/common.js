import num from './num'
import UtilObj from '@/util/obj'

export default {
  isEmpty: UtilObj.isEmpty,
  checkObjHasProp: UtilObj.checkObjHasProp,

  byteToUnit: (byteSize, returnUnit = 'MB', withUnit = true, digits = 1) => {
    let formattedSize = byteSize
    const lowerUnit = returnUnit.toLowerCase()
    const units = ['b', 'kb', 'mb', 'gb']
    const targetUnitIdx = units.findIndex(unit => unit === lowerUnit)
    if (targetUnitIdx != -1) {
      for (let i = 0, n = targetUnitIdx; i < n; i++) {
        formattedSize = formattedSize / 1024
      }
      formattedSize = num.orgFloor(formattedSize, digits)
      if (withUnit) {
        formattedSize += returnUnit
      }
      return formattedSize
    }
  },
}
