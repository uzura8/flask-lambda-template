<template>
<div>
  <b-field
    :label="$t('common.url')"
    :type="checkEmpty(errors.url) ? '' : 'is-danger'"
    :message="checkEmpty(errors.url) ? '' : errors.url[0]"
    class="mt-5"
  >
    <b-input
      v-model="url"
      @blur="validate('url')"
    ></b-input>
  </b-field>

  <b-field
    :label="$t('form.isViaJumpPageLabel')"
    :type="checkEmpty(errors.isViaJumpPage) ? '' : 'is-danger'"
    :message="checkEmpty(errors.isViaJumpPage) ? '' : errors.isViaJumpPage[0]"
    class="mt-5"
  >
    <b-checkbox v-model="isViaJumpPage">
      {{ $t('form.viaJumpPage') }}
    </b-checkbox>
  </b-field>

  <b-field
    :label="$t('common.name')"
    :type="checkEmpty(errors.name) ? '' : 'is-danger'"
    :message="checkEmpty(errors.name) ? '' : errors.name[0]"
    class="mt-5"
  >
    <b-input
      v-model="name"
      @blur="validate('name')"
    ></b-input>
  </b-field>

  <b-field
    :label="$t('common.description')"
    :type="checkEmpty(errors.description) ? '' : 'is-danger'"
    :message="checkEmpty(errors.description) ? '' : errors.description[0]"
  >
    <b-input
      type="textarea"
      v-model="description"
      @blur="validate('description')"
      ref="inputDescription"
    ></b-input>
  </b-field>

  <div
    v-if="globalError"
    class="block has-text-danger mt-5"
  >{{ globalError }}</div>

  <div class="field mt-5">
    <div class="control">
      <button
        class="button is-warning"
        :disabled="isLoading || hasErrors"
        @click="save(false)"
        v-text="isEdit ? $t('common.edit') : $t('common.create')"
      ></button>
    </div>
  </div>

  <div class="field">
    <div class="control">
      <button
        class="button is-light"
        :disabled="isLoading"
        @click="cancel"
        v-text="$t('common.cancel')"
      ></button>
    </div>
  </div>
</div>
</template>
<script>
import str from '@/util/str'
import { Admin } from '@/api'
import config from '@/config/config'

export default{
  name: 'AdminPostForm',

  components: {
  },

  props: {
    shortenUrl: {
      type: Object,
      default: null,
    },
  },

  data(){
    return {
      name: '',
      description: '',
      url: '',
      isViaJumpPage: false,
      fieldKeys: ['name', 'description', 'url', 'isViaJumpPage'],
      errors: [],
    }
  },

  computed: {
    isEdit() {
      return this.shortenUrl != null
    },

    isEmptyRequiredFields() {
      if (!this.checkEmpty(this.url)) return false
      return true
    },

    hasErrors() {
      if (this.globalError) return true

      let hasError = false
      Object.keys(this.errors).map(field => {
        if (this.errors[field].length > 0) hasError = true
      })
      return hasError
    },
  },

  watch: {
  },

  async created() {
    if (this.isEdit === true) {
      this.setShortenUrl()
    }
  },

  methods: {
    setShortenUrl() {
      this.name = this.shortenUrl.name != null ? String(this.shortenUrl.name) : ''
      this.url = this.shortenUrl.url != null ? String(this.shortenUrl.url) : ''
      this.description = this.shortenUrl.description != null ? String(this.shortenUrl.description) : ''
      this.isViaJumpPage = this.shortenUrl.isViaJumpPage
    },

    resetInputs() {
      this.url = ''
      this.name = ''
      this.description = ''
      this.isViaJumpPage = false
    },

    async save(forcePublish = false) {
      this.validateAll()
      if (this.hasErrors) return

      try {
        let vals = {}
        vals.url = this.url
        vals.name = this.name
        vals.description = this.description
        vals.isViaJumpPage = this.isViaJumpPage
        this.$store.dispatch('setLoading', true)
        let res
        if (this.isEdit) {
          res = await Admin.updateShortenUrl(this.serviceId, this.shortenUrl.urlId, vals, this.adminUserToken)
        } else {
          res = await Admin.createShortenUrl(this.serviceId, vals, this.adminUserToken)
          this.$store.dispatch('resetAdminShortenUrlsPager', false)
        }
        this.$store.dispatch('setLoading', false)
        //this.$emit('posted', res)
        this.resetInputs()
        this.$router.push(`/admin/shorten-urls/${this.serviceId}/${res.urlId}`)
      } catch (err) {
        console.log(err);//!!!!!!
        this.$store.dispatch('setLoading', false)
        if (this.checkResponseHasErrorMessage(err, true)) {
          this.setErrors(err.response.data.errors)
        }
        const msgKey = this.isEdit ? 'Edit failed' : 'Create failed'
        this.handleApiError(err, this.$t(`msg["${msgKey}"]`))
      }
    },

    cancel() {
      this.resetInputs()
      this.$router.push(`/admin/shorten-urls/${this.serviceId}`)
    },

    validateAll() {
      this.fieldKeys.map(field => {
        this.validate(field)
      })
      if (this.hasErrors) {
        this.globalError = this.$t("msg['Correct inputs with error']")
      } else if (this.isEmptyRequiredFields) {
        this.globalError = this.$t("msg['Input required']")
      }
    },

    validate(field) {
      const key = 'validate' + str.capitalize(field)
      this[key]()
    },

    validateName() {
      this.initError('name')
      if (this.name === null) this.name = ''
      this.name = this.name.trim()
    },

    validateUrl() {
      this.initError('url')
      if (this.url === null) this.url = ''
      this.url = this.url.trim()
      if (this.checkEmpty(this.url)) this.errors.url.push(this.$t('msg["Input required"]'))
      if (str.checkUrl(this.url) === false) this.errors.url.push(this.$t('msg.InvalidInput'))
    },

    validateDescription() {
      this.initError('description')
      if (this.description === null) this.description = ''
      this.description = this.description.trimEnd()
    },

    validateIsViaJumpPage() {
      this.initError('isViaJumpPage')
    },
  },
}
</script>

