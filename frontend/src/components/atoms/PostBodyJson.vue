<template>
  <div class="post-body-json">
    <pre><code class="language-json">{{ formattedBodyJson }}</code></pre>
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
    bodyJson: {
      type: Object,
      default: null,
    },
  },

  data(){
    return {
    }
  },

  computed: {
    formattedBodyJson() {
      return JSON.stringify(this.bodyJson, null, "  ").trim()
    },
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

.post-body-json {
  @import "scss/browser-default.scss";
  pre {
    padding: 0.5rem;
  }
}
</style>

