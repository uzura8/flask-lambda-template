export default {
  nowUtime() {
    const date = new Date()
    const now = date.getTime()
    return  Math.floor(now / 1000)
  },
}
