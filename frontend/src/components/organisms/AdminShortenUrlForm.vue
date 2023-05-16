<template>
<div>
  <b-field
    :label="$t('common.locationTo')"
    :type="checkEmpty(errors.url) ? '' : 'is-danger'"
    placeholder="https://example.com/"
    :message="checkEmpty(errors.url) ? '' : errors.url[0]"
    class="mt-5"
  >
    <b-input
      v-model="url"
      @blur="validate('url')"
    ></b-input>
  </b-field>

  <b-field
    v-if="isSetJumpPageConfigs"
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
    :label="$t('common.paramsFor', {target: $t('term.accessAnalysis')})"
    :message="checkEmpty(errors.paramKeyValue) ? '' : errors.paramKeyValue[0]"
    :type="checkEmpty(errors.paramKeyValue) ? '' : 'is-danger'"
    grouped
  >
    <b-field
      label="paramKey"
      :message="checkEmpty(errors.paramKey) ? '' : errors.paramKey[0]"
      :type="checkEmpty(errors.paramKey) ? '' : 'is-danger'"
    >
      <b-input
        v-model="paramKey"
        @blur="validate('paramKey')"
      ></b-input>
    </b-field>
    <b-field
      label="paramValue"
      :message="checkEmpty(errors.paramValue) ? '' : errors.paramValue[0]"
      :type="checkEmpty(errors.ParamValue) ? '' : 'is-danger'"
    >
      <b-input
        v-model="paramValue"
        @blur="validate('paramValue')"
        expanded
      ></b-input>
    </b-field>
  </b-field>

  <div
    v-if="generatedUrl"
    class="p-3 mt-4 has-background-light u-wrap"
  >
    <h5 class="title is-6">{{ $t('term.generateUrl') }}</h5>
    <div>
      <a :href="generatedUrl" target="_blank">{{ generatedUrl }}</a>
    </div>
  </div>

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
import common from '@/util/common'
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
      paramKey: '',
      paramValue: '',
      isViaJumpPage: false,
      fieldKeys: ['name', 'description', 'url', 'isViaJumpPage', 'paramKey', 'paramValue'],
      errors: [],
      serviceConfigs: null,
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

    parsedUrl() {
      if (this.checkEmpty(this.url) === true) return
      return new URL(this.url)
    },

    isSetJumpPageConfigs() {
      if (!this.serviceConfigs) return false
      if (common.checkObjHasProp(this.serviceConfigs, 'jumpPageUrl') === false) return false
      if (!this.serviceConfigs.jumpPageUrl) return false
      if (!this.serviceConfigs.jumpPageParamKey) return false
      return true
    },

    generatedUrl() {
      if (!this.serviceConfigs) return ''
      if (this.checkEmpty(this.url) === true) return ''
      if (str.checkUrl(this.url) === false) return ''

      let addedQuery = ''
      if (this.paramKey && this.paramValue) {
        addedQuery = `${this.paramKey}=${this.paramValue}`
      }
      const hash = this.parsedUrl.hash

      let items = []
      if (this.isViaJumpPage) {
        items = [
          this.parsedUrl.origin,
          this.parsedUrl.pathname,
          this.parsedUrl.search,
          hash,
        ]
        const targetUrl = items.join('')

        const parsedUrl = new URL(this.serviceConfigs.jumpPageUrl)
        const delimitter = parsedUrl.search ? '&' : '?'
        items = [
          this.serviceConfigs.jumpPageUrl,
          delimitter,
          this.serviceConfigs.jumpPageParamKey,
          '=',
          encodeURIComponent(targetUrl),
          addedQuery ? '&' : '',
          addedQuery,
        ]
      } else {
        let delimitter = ''
        if (addedQuery) {
          delimitter = this.parsedUrl.search ? '&' : '?'
        }
        items = [
          this.parsedUrl.origin,
          this.parsedUrl.pathname,
          this.parsedUrl.search, delimitter, addedQuery,
          hash,
        ]
      }
      return items.join('')
    },

    hasErrors() {
      if (this.globalError) return true

      let hasError = false
      Object.keys(this.errors).map(field => {
        if (this.errors[field].length > 0) hasError = true
      })
      if (this.errors.paramKeyValue.length > 0) hasError = true
      return hasError
    },
  },

  watch: {
  },

  async created() {
    this.initError('paramKeyValue')
    if (this.isEdit === true) {
      this.setShortenUrl()
    }
    await this.setServiceConfigs()
  },

  methods: {
    setShortenUrl() {
      this.name = this.shortenUrl.name != null ? String(this.shortenUrl.name) : ''
      this.url = this.shortenUrl.url != null ? String(this.shortenUrl.url) : ''
      this.description = this.shortenUrl.description != null ? String(this.shortenUrl.description) : ''
      this.isViaJumpPage = this.shortenUrl.isViaJumpPage
      this.paramKey = this.shortenUrl.paramKey != null ? String(this.shortenUrl.paramKey) : ''
      this.paramValue = this.shortenUrl.paramValue != null ? String(this.shortenUrl.paramValue) : ''
    },

    resetInputs() {
      this.url = ''
      this.name = ''
      this.description = ''
      this.isViaJumpPage = false
      this.paramKey = ''
      this.paramValue = ''
    },

    async setServiceConfigs() {
      try {
        this.$store.dispatch('setLoading', true)
        const service = await Admin.getServices(this.serviceId, null, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
        if (common.checkObjHasProp(service, 'configs')) {
          this.serviceConfigs = service.configs
        }
        if (common.checkObjHasProp(this.serviceConfigs, 'analysisParamKeyDefault')) {
          if (!this.paramKey) this.paramKey = this.serviceConfigs.analysisParamKeyDefault
        }
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
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
        vals.paramKey = this.paramKey
        vals.paramValue = this.paramValue
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
        this.debugOutput(err)
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

      if ((this.paramKey && !this.paramValue) || (!this.paramKey && this.paramValue)) {
        this.errors.paramKeyValue.push(this.$t('msg.inputRequiredBoth'))
      }

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

    validateParamKey() {
      this.initError('paramKey')
      this.$set(this.errors, 'paramKeyValue', [])
      if (this.paramKey === null) this.paramKey = ''
      this.paramKey = this.paramKey.trim()
      if (this.paramKey && str.checkKeyString(this.paramKey) === false) {
        this.errors.paramKey.push(this.$t('msg.InvalidInput'))
      }
    },

    validateParamValue() {
      this.initError('paramValue')
      this.$set(this.errors, 'paramKeyValue', [])
      if (this.paramValue === null) this.paramValue = ''
      this.paramValue = this.paramValue.trim()
    },
  },
}
</script>

