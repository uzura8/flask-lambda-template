<template>
<div>
  <editor
    :value="value"
    :api-key="tinyMCEApiKey"
    :init="editorOptions"
    @input="changeValue"
  ></editor>
</div>
</template>
<script>
import config from '@/config/config'
import Editor from '@tinymce/tinymce-vue'

export default{
  name: 'RichTextEditor',

  components: {
    'editor': Editor,
  },

  props: {
    value: {
      type: String,
      default: '',
    },
  },

  data(){
    return {
      editorOptions: {
        height: 500,
        language: 'ja',
        forced_root_block : false,
        menubar: true,
        plugins: [
          'emoticons','hr', 'code',
          'lists','link','preview','anchor','visualblocks',
          'table','help', 'fullscreen'
        ],
        toolbar:
          'undo redo | bold italic backcolor forecolor removeformat | \
          alignleft aligncenter alignright alignjustify | \
          bullist numlist outdent indent | hr table link emoticons | visualblocks fullscreen preview code help'
      },
    }
  },

  computed: {
    tinyMCEApiKey() {
      return config.tinyMCEApiKey
    },
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

