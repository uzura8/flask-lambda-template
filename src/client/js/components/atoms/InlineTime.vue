<template>
<span>
  <time
    v-if="datetime"
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
}
</script>

