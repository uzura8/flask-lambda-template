function checkObjHasProp(obj, prop, checkEmpty=false) {
  if (typeof obj !== 'object') return false
  if (Array.isArray(obj) === true) return false
  if (obj.hasOwnProperty(prop) === false) return false
  if (obj[prop] == null) return false
  if (checkEmpty === false) return true
  return isEmpty(obj[prop]) === false
}

function isEmpty(data) {
  if (data === null) return true;
  if (data === undefined) return true;
  if (data === false) return true;
  if (data === '') return true;
  if (data === '0') return true;
  if (data === 0) return true;
  if (typeof data === 'object') {
    if (Array.isArray(data)) return data.length === 0;
    if (Object.keys(data).length > 0) return false;
    if (
      typeof Object.getOwnPropertySymbols !== 'undefined' &&
      Object.getOwnPropertySymbols(data).length > 0
    )
      return false;
    if (data.valueOf().length !== undefined)
      return data.valueOf().length === 0;
    if (typeof data.valueOf() !== 'object') return this.isEmpty(data.valueOf());
  }
  return false;
}

export default {
  checkObjHasProp: checkObjHasProp,
  isEmpty: isEmpty,

  isObject(obj) {
    return typeof obj === 'object' && obj !== null && !Array.isArray(obj)
  },

  getVal(obj, key, defval = null) {
    if (checkObjHasProp(obj, key) === true) return obj[key]
    return defval
  },

  checkObjItemsNotEmpty(obj, reqKeys=[], checkEmpty=false) {
    if (isEmpty(obj) === true) return false

    if (reqKeys) {
      for (let i = 0, n = reqKeys.length; i < n; i++) {
        let key = reqKeys[i]
        if (checkObjHasProp(obj, key) === false) return false
        if (checkEmpty === true && !obj[key]) return false
      }
    } else {
      for (let key in obj) {
        if (obj.hasOwnProperty(key) === false) continue
        if (checkEmpty === true && !obj[key]) return false
      }
    }
    return true
  },

  isEqual(obj1, obj2) {
    if (obj1 == null) return false
    if (obj2 == null) return false
    if (typeof obj1 !== 'object') return false
    if (typeof obj2 !== 'object') return false

    if (Object.keys(obj1).length !== Object.keys(obj2).length) {
      return false
    }

    for (let key in obj1) {
      if (obj1.hasOwnProperty(key) && obj1[key] !== obj2[key]) {
        return false
      }
    }
    return true
  },
}
