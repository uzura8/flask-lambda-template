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
      bodyMarkdown: '',
    }
  },

  computed: {
  },

  created() {
    marked.setOptions({
      breaks: true,
      highlight: (code, lang) => {
        return hljs.highlightAuto(code, [lang]).value
      },
    })
  },

  mounted() {
    this.bodyMarkdown = marked(this.body)
    window.hljs.highlightAll()
  },

  methods: {
  },
}
</script>
<style>
@import "~highlight.js/styles/atom-one-dark.css";

.post-body {
  @import "@/scss/browser-default.scss";
  pre {
    padding: 1.25rem 1.5rem;
  }
}
</style>

