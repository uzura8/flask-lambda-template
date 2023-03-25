<template>
  <div
    v-html="bodyMarkdown"
    class="post-body"
  >
  </div>
</template>
<script>
import marked from 'marked'
import hljs from 'highlight.js'
window.hljs = hljs

export default{
  name: 'PostBodyMarkdown.',

  components: {
  },

  props: {
    body: {
      type: String,
      default: '',
    },
  },

  data(){
    return {
    }
  },

  computed: {
    bodyMarkdown() {
      return marked(this.body)
    },
  },

  created() {
    marked.setOptions({ breaks: true })
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
  pre {
    padding: 0 0;
  }
}
</style>

