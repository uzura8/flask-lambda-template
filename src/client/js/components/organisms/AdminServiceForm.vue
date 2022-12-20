<template>
<div>
  <b-field
    v-if="isEdit"
    label="serviceId"
  >{{ service.serviceId }}</b-field>
  <b-field
    v-else
    label="serviceId"
    :type="checkEmpty(errors.serviceIdInput) ? '' : 'is-danger'"
    :message="checkEmpty(errors.serviceIdInput) ? '' : errors.serviceIdInput[0]"
  >
    <b-input
      v-model="serviceIdInput"
      @blur="validate('serviceIdInput')"
    ></b-input>
  </b-field>

  <b-field
    label="label"
    :type="checkEmpty(errors.label) ? '' : 'is-danger'"
    :message="checkEmpty(errors.label) ? '' : errors.label[0]"
  >
    <b-input
      v-model="label"
      @blur="validate('label')"
    ></b-input>
  </b-field>

  <b-field
    class="mb-0"
    :label="$t('form.functionToApply')"
  >
    <b-checkbox
      v-model="functions"
      native-value="post"
    >{{ $t('term.availableFunctions.post') }}</b-checkbox>
  </b-field>

  <div
    v-if="functions.includes('post')"
    class="pl-5 pt-2 pb-4"
  >
    <b-field
      :label="$t('form.frontendPostDetailUrlPrefix')"
      :type="checkEmpty(errors.frontendPostDetailUrlPrefix) ? '' : 'is-danger'"
      :message="checkEmpty(errors.frontendPostDetailUrlPrefix) ? '' : errors.frontendPostDetailUrlPrefix[0]"
    >
      <b-input
        v-model="frontendPostDetailUrlPrefix"
        @blur="validate('frontendPostDetailUrlPrefix')"
      ></b-input>
    </b-field>
  </div>

  <b-field class="mb-0">
    <b-checkbox
      v-model="functions"
      native-value="urlShortener"
    >{{ $t('term.availableFunctions.urlShortener') }}</b-checkbox>
  </b-field>

  <div
    v-if="functions.includes('urlShortener')"
    class="pl-5 pt-2 pb-4"
  >
    <b-field grouped>
      <b-field
        :label="$t('form.jumpPageUrl')"
        :type="checkEmpty(errors.jumpPageUrl) ? '' : 'is-danger'"
        :message="checkEmpty(errors.jumpPageUrl) ? '' : errors.jumpPageUrl[0]"
        expanded
      >
        <b-input
          v-model="jumpPageUrl"
          @blur="validate('jumpPageUrl')"
        ></b-input>
      </b-field>

      <b-field
        :label="$t('form.jumpPageParamKey')"
        :type="checkEmpty(errors.jumpPageParamKey) ? '' : 'is-danger'"
        :message="checkEmpty(errors.jumpPageParamKey) ? '' : errors.jumpPageParamKey[0]"
      >
        <b-input
          v-model="jumpPageParamKey"
          @blur="validate('jumpPageParamKey')"
        ></b-input>
      </b-field>
    </b-field>

    <b-field
      :label="$t('form.analysisParamKeyDefault')"
      :type="checkEmpty(errors.analysisParamKeyDefault) ? '' : 'is-danger'"
      :message="checkEmpty(errors.analysisParamKeyDefault) ? '' : errors.analysisParamKeyDefault[0]"
    >
      <b-input
        v-model="analysisParamKeyDefault"
        @blur="validate('analysisParamKeyDefault')"
      ></b-input>
    </b-field>
  </div>

  <div
    v-if="globalError"
    class="block has-text-danger mt-5 mb-0"
  >{{ globalError }}</div>

  <div class="field mt-5">
    <div class="control">
      <button
        class="button is-warning"
        :disabled="isLoading || hasErrors"
        @click="save(false)"
        v-text="$t('common.edit')"
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
import config from '@/config/config'
import { Admin } from '@/api'

export default{
  name: 'AdminServiceForm',

  components: {
  },

  props: {
    service: {
      type: Object,
      default: null,
    },
  },

  data(){
    return {
      serviceIdInput: '',
      label: '',
      functions: [],
      frontendPostDetailUrlPrefix: '',
      jumpPageUrl: '',
      jumpPageParamKey: '',
      analysisParamKeyDefault: '',
      fieldKeys: [
        'serviceIdInput',
        'label',
        'functions',
        'frontendPostDetailUrlPrefix',
        'jumpPageUrl',
        'jumpPageParamKey',
        'analysisParamKeyDefault',
      ],
    }
  },

  computed: {
    isEdit() {
      return this.service != null
    },

    isEmptyAllFields() {
      if (!this.isEdit && !this.checkEmpty(this.serviceIdInput)) return false
      if (!this.checkEmpty(this.label)) return false
      if (!this.checkEmpty(this.frontendPostDetailUrlPrefix)) return false
      if (!this.checkEmpty(this.jumpPageUrl)) return false
      if (!this.checkEmpty(this.jumpPageParamKey)) return false
      if (!this.checkEmpty(this.analysisParamKeyDefault)) return false
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

  created() {
    this.setService()
  },

  methods: {
    setService() {
      if (!this.isEdit) return
      this.label = this.service.label != null ? String(this.service.label) : ''
      this.functions = this.service.functions != null ? this.service.functions : []
      if (common.checkObjHasProp(this.service, 'configs')) {
        this.frontendPostDetailUrlPrefix = this.service.configs.frontendPostDetailUrlPrefix != null ? String(this.service.configs.frontendPostDetailUrlPrefix) : ''
        this.jumpPageUrl = this.service.configs.jumpPageUrl != null ? String(this.service.configs.jumpPageUrl) : ''
        this.jumpPageParamKey = this.service.configs.jumpPageParamKey != null ? String(this.service.configs.jumpPageParamKey) : ''
        this.analysisParamKeyDefault = this.service.configs.analysisParamKeyDefault != null ? String(this.service.configs.analysisParamKeyDefault) : ''
      } else {
        this.frontendPostDetailUrlPrefix = ''
        this.jumpPageUrl = ''
        this.jumpPageParamKey = ''
        this.analysisParamKeyDefault = ''
      }
    },

    resetInputs() {
      this.serviceIdInput = ''
      this.label = ''
      this.functions = []
      this.frontendPostDetailUrlPrefix = ''
      this.jumpPageUrl = ''
      this.jumpPageParamKey = ''
      this.analysisParamKeyDefault = ''
    },

    async save(forcePublish = false) {
      this.validateAll()
      if (this.hasErrors) return

      try {
        let service
        let vals = {}
        if (!this.isEdit) vals.serviceId = this.serviceIdInput
        vals.label = this.label
        vals.functions = this.functions

        vals.configs = {}
        vals.configs.frontendPostDetailUrlPrefix = this.frontendPostDetailUrlPrefix
        if (this.jumpPageUrl) vals.configs.jumpPageUrl = this.jumpPageUrl
        if (this.jumpPageParamKey) vals.configs.jumpPageParamKey = this.jumpPageParamKey
        vals.configs.analysisParamKeyDefault = this.analysisParamKeyDefault

        this.$store.dispatch('setLoading', true)
        let res
        if (this.isEdit) {
          res = await Admin.updateService(this.serviceId, vals, this.adminUserToken)
        } else {
          res = await Admin.createService(vals, this.adminUserToken)
        }
        this.$store.dispatch('setLoading', false)
        this.resetInputs()
        this.$router.push('/admin/services')
      } catch (err) {
        console.log(err)
        this.$store.dispatch('setLoading', false)
        if (this.checkResponseHasErrorMessage(err, true)) {
          this.setErrors(err.response.data.errors)
        }
        const msgKey = this.isEdit ? 'Edit failed' : 'Create failed'
        this.handleApiError(err, this.$t(`msg["${msgKey}"]`))
      }
    },

    async checkServiceIdExists(slug) {
      try {
        this.$store.dispatch('setLoading', true)
        await Admin.getServices(this.serviceIdInput, null, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
        return true
      } catch (err) {
        this.$store.dispatch('setLoading', false)
        if (err.response == null || err.response.status !== 404) {
          this.handleApiError(err)
        }
        return false
      }
    },

    cancel() {
      this.resetInputs()
      this.$router.push(`/admin/services`)
    },

    validateAll() {
      this.fieldKeys.map(field => {
        this.validate(field)
      })
      if (!this.checkEmpty(this.jumpPageUrl) && this.checkEmpty(this.jumpPageParamKey)
        || this.checkEmpty(this.jumpPageUrl) && !this.checkEmpty(this.jumpPageParamKey)) {
        if (this.checkEmpty(this.jumpPageUrl)) this.errors.jumpPageUrl.push(this.$t('msg["Input required"]'))
        if (this.checkEmpty(this.jumpPageParamKey)) this.errors.jumpPageParamKey.push(this.$t('msg["Input required"]'))
      }
      if (this.hasErrors) {
        this.globalError = this.$t("msg['Correct inputs with error']")
      } else if (this.isEmptyAllFields) {
        this.globalError = this.$t("msg['Input required']")
      }
    },

    validate(field) {
      const key = 'validate' + str.capitalize(field)
      this[key]()
    },

    async validateServiceIdInput() {
      if (this.isEdit) return

      this.initError('serviceIdInput')
      if (this.serviceIdInput === null) this.serviceIdInput = ''
      this.serviceIdInput = this.serviceIdInput.trim()
      if (this.checkEmpty(this.serviceIdInput)) {
        this.errors.serviceIdInput.push(this.$t('msg["Input required"]'))
      } else if (str.checkSlug(this.serviceIdInput) === false) {
        this.errors.serviceIdInput.push(this.$t('msg.InvalidInput'))
      } else if (this.isEdit === false || this.serviceIdInput !== this.service.serviceId) {
        const isExists = await this.checkServiceIdExists(this.serviceIdInput)
        if (isExists) {
          this.errors.serviceIdInput.push(this.$t('msg["Already in use"]'))
        }
      }
    },

    validateLabel() {
      this.initError('label')
      if (this.label === null) this.label = ''
      this.label = this.label.trim()
      if (this.checkEmpty(this.label)) this.errors.label.push(this.$t('msg["Input required"]'))
    },

    validateFunctions() {
      const allowed = config.availableFunctions
      this.initError('functions')
      if (this.functions == null) this.functions = []
      if (this.functions) {
        let hasError = false
        this.functions.map((item) => {
          if (hasError === true) return
          if (allowed.includes(item) === false) {
            hasError = true
          }
        })
        if (hasError === true) {
          this.globalError = this.$t('msg.invalidError', {field: this.$t('form.functionToApply')})
        }
      }
    },

    validateFrontendPostDetailUrlPrefix() {
      this.initError('frontendPostDetailUrlPrefix')
      if (this.frontendPostDetailUrlPrefix === null) this.frontendPostDetailUrlPrefix = ''
      this.frontendPostDetailUrlPrefix = this.frontendPostDetailUrlPrefix.trim()
    },

    validateJumpPageUrl() {
      this.initError('jumpPageUrl')
      if (this.jumpPageUrl === null) this.jumpPageUrl = ''
      this.jumpPageUrl = this.jumpPageUrl.trim()
      if (this.checkEmpty(this.jumpPageUrl) === false) {
        if (str.checkUrl(this.jumpPageUrl) === false) this.errors.jumpPageUrl.push(this.$t('msg.InvalidInput'))
      }
    },

    validateJumpPageParamKey() {
      this.initError('jumpPageParamKey')
      if (this.jumpPageParamKey === null) this.jumpPageParamKey = ''
      this.jumpPageParamKey = this.jumpPageParamKey.trim()
    },

    validateAnalysisParamKeyDefault() {
      this.initError('analysisParamKeyDefault')
      if (this.analysisParamKeyDefault === null) this.analysisParamKeyDefault = ''
      this.analysisParamKeyDefault = this.analysisParamKeyDefault.trim()
    },
  },
}
</script>

