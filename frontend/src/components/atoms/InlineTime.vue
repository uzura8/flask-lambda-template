<template>
<span>
  <time
    v-if="isEmptyDatetime === false"
    itemprop="time"
    :datetime="datetime | dateFormat(format)"
    :class="timeClass"
  >{{ datetime | dateFormat }}</time>
  <span v-else>-</span>
</span>
</template>
<script>
export default{
  name: 'InlineTime',

  props: {
    datetime: {
      type: String,
      default: '',
    },

    format: {
      type: String,
      default: '',
    },

    timeClass: {
      type: String,
      default: '',
    },
  },

  computed: {
    isEmptyDatetime() {
      if (this.checkEmpty(this.datetime)) return true
      if (this.datetime === 'None') return true
      return false
    },
  },
}
</script>

