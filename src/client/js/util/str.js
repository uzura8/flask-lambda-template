const numFormat = function(num) {
  num = parseInt(num)
  if (isNaN(num)) return 0
  return String(num).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, '$1,');
}

export default {
  substr: (text, len, truncation='') => {
    const text_array = text.split('')
    let count = 0
    let str = ''
    for (let i = 0, m = text_array.length; i < m; i++) {
      let n = escape(text_array[i])
      if (n.length < 4) {
        count++
      } else {
        count += 2;
      }
      if (count > len) {
        return str + truncation
      }
      str += text.charAt(i)
    }
    return text
  },

  capitalize: (text) => {
    return text.slice(0, 1).toUpperCase() + text.slice(1)
  },

  ltrimChar: function(str, anyChar) {
    return str.replace(new RegExp('^' + anyChar, 'g'),'')
  },

  rtrimChar: function(str, anyChar) {
    return str.replace(new RegExp(anyChar + '+$', 'g'),'')
  },

  trimChar: function(str, anyChar) {
    return str.replace(new RegExp('^' + anyChar + '+|' + anyChar + '+$', 'g'),'')
  },

  numFormat: function(num) {
    return numFormat(num)
  },

  bytesFormat: function(num) {
    let formatted
    let unit = 'B'
    let count = 0

    num = parseInt(num)
    if (isNaN(num)) return `0 ${unit}`

    if (num < 1024) {
      formatted = numFormat(num)
      return `${formatted} ${unit}`
    } else if (num < 1024 ** 2) {
      count = 1
      unit = 'KB'
    } else if (num < 1024 ** 3) {
      count = 2
      unit = 'MB'
    } else if (num < 1024 ** 4) {
      count = 3
      unit = 'GB'
    } else {
      formatted = numFormat(num)
      return `${formatted} ${unit}`
    }

    formatted = num
    for (let i = 0; i < count; i++) {
      formatted = formatted / 1024
    }
    formatted = Math.floor(formatted * 100) / 100

    return `${formatted} ${unit}`
  },

  convObjToStr: function(obj, delimitter=',') {
    let items = []
    Object.keys(obj).map((key) => {
      items.push(`${key}:${obj[key]}`)
    })
    return items.join(delimitter)
  },

  nl2br: function(str) {
    if (str == null) return ''
    str = str.replace(/\r\n/g, '<br />')
    str = str.replace(/(\n|\r)/g, '<br />')
    return str
  },

  url2link: function(str) {
    if (str == null) return ''
    const pattern = /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gim
    return str.replace(pattern, '<a href="$1" target="_blank">$1</a>')
  },

  escapeHtml: function(str) {
    if (str == null) return ''
    return str.replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  },

  convSnakeToCamel: function(p) {
    return p.replace(/_./g, (s) => {
      return s.charAt(1).toUpperCase()
    })
  },

  convCamelToSnake: function(p){
    return p.replace(/([A-Z])/g, (s) => {
      return '_' + s.charAt(0).toLowerCase();
    })
  },

  getRandStr: function(num, chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-') {
    let res = ''
    for (let i = 0; i < num; i++) {
      res += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    return res
  },

  checkEmail: function(text) {
    const regexp = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    return regexp.test(text)
  },

  checkUrl: function(text) {
    const regexp = /^https?:\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+$/
    return regexp.test(text)
  },

  checkTel: function(text) {
    const regexp = /^(0[5-9]0[0-9]{8}|0[1-9][1-9][0-9]{7})$/
    return regexp.test(text)
  },

  checkSlug: function(text) {
    const regexp = /^[0-9a-z\-]+$/
    return regexp.test(text)
  },

  checkServiceUsername: function(text, acceptSymbols = []) {
    let acceptChars = '0-9a-z'
    if (acceptSymbols.length) {
      acceptChars += acceptSymbols.join('')
    }
    const strCombRegex = `^[${acceptChars}]+$`
    const regexp = new RegExp(strCombRegex)
    return regexp.test(text)
  },

  checkExtension(str, acceptedExts) {
    const acceptedExtsStr = acceptedExts.join('|')
    const pattern = `\.(${acceptedExtsStr})$`
    const regexp = new RegExp(pattern, 'i')
    return regexp.test(str)
  },
}
