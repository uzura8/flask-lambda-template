<template>
  <div
    v-html="body"
    class="post-body"
  >
  </div>
</template>
<script>
import hljs from 'highlight.js'
window.hljs = hljs

export default{
  name: 'PostBody',

  components: {
  },

  props: {
    body: {
      type: String,
      default: '',
    },
    //bodyFormat: {
    //  type: String,
    //  default: 'html',
    //}
  },

  data(){
    return {
    }
  },

  computed: {
  },

  mounted() {
    window.hljs.highlightAll()
  },

  methods: {
  },
}
</script>
<style>
@import "~highlight.js/styles/atom-one-dark.css";

.post-body {
  @import "../scss/browser-default.scss";
}
</style>

