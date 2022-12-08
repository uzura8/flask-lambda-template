<template>
<div class="columns is-1 mt-0 mb-0">
  <div class="column is-6">
    <div>
      <b-input
        v-model="url"
        @blur="validateUrl()"
        placeholder="URL"
      ></b-input>
    </div>
    <div
      v-if="checkEmpty(errors.url) === false"
      class="has-text-danger"
    >{{ errors.url }}</div>
  </div>
  <div class="column is-5">
    <div>
      <b-input
        v-model="label"
        @blur="validateLabel()"
        :placeholder="$t('common.dispLabel')"
      ></b-input>
    </div>
    <div
      v-if="checkEmpty(errors.label) === false"
      class="has-text-danger"
    >{{ errors.label }}</div>
  </div>
  <div class="column is-1">
    <button
      class="button is-light is-small btn-delete"
      @click="deleteItem"
    >
      <span class="icon">
        <i class="fas fa-times-circle"></i>
      </span>
    </button>
  </div>
</div>
</template>
<script>
import str from '@/util/str'

export default{
  name: 'FormLinks',

  components: {
  },

  props: {
    link: {
      type: Object,
      default: null,
    },
  },

  data(){
    return {
      url: '',
      label: '',
      errors: {
        url: '',
        label: '',
      },
    }
  },

  computed: {
    hasError() {
      if (this.checkEmpty(this.errors.url) === false) return true
      if (this.checkEmpty(this.errors.label) === false) return true
      return false
    },

    linkId() {
      return this.link.id
    },
  },

  watch: {
    url(vals) {
      this.emitValue()
    },

    label(vals) {
      this.emitValue()
    },

    hasError(vals) {
      this.$emit('has-error', vals)
    },
  },

  created() {
    if ('url' in this.link && this.link.url) {
      this.url = this.link.url
    }
    if ('label' in this.link && this.link.label) {
      this.label = this.link.label
    }
  },

  methods: {
    deleteItem() {
      this.$emit('delete', this.linkId)
    },

    emitValue() {
      this.$emit('updated-link', {
        id: this.linkId,
        url: this.url,
        label: this.label,
      })
    },

    validateUrl() {
      this.errors.url = ''
      this.url = this.url.trim()
      if (this.checkEmpty(this.url)) {
        this.errors.url = this.$t('msg["Input required"]')
      } else if (str.checkUrl(this.url) === false) {
        this.errors.url = this.$t('msg.invalidError', { field: 'URL' })
      }
    },

    validateLabel() {
      this.errors.label = ''
      this.label = this.label.trim()
      this.validateUrl()
    },
  },
}
</script>

