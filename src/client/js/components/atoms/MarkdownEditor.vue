<template>
<div>
  <vue-easymde
    ref="markdownEditor"
    :highlight="true"
    :value="value"
    @update:modelValue="changeValue"
  ></vue-easymde>
</div>
</template>
<script>
import hljs from 'highlight.js'
import VueEasymde from 'vue-easymde'

window.hljs = hljs

export default{
  name: 'MarkdownEditor',

  components: {
    VueEasymde,
  },

  props: {
    value: {
      type: String,
      default: '',
    },
  },

  data(){
    return {
    }
  },

  computed: {
  },

  watch: {
  },

  created() {
  },

  methods: {
    changeValue(event) {
      this.$emit('input', event)
    },
  },
}
</script>
<style>
@import "~easymde/dist/easymde.min.css";
@import "~highlight.js/styles/atom-one-dark.css";
.editor-preview {
  &.editor-preview-active {
    @import "@/../scss/browser-default.scss";
  }
}
.editor-preview-side {
  &.editor-preview-active-side {
    @import "@/../scss/browser-default.scss";
  }
}
</style>

