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

  <div
    v-if="globalError"
    class="block has-text-danger"
  >{{ globalError }}</div>

  <div class="field">
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
import str from '@/util/str'
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
      fieldKeys: ['serviceIdInput', 'label'],
    }
  },

  computed: {
    isEdit() {
      return this.service != null
    },

    isEmptyAllFields() {
      if (!this.isEdit && !this.checkEmpty(this.serviceIdInput)) return false
      if (!this.checkEmpty(this.label)) return false
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
    },

    resetInputs() {
      this.serviceIdInput = ''
      this.label = ''
    },

    async save(forcePublish = false) {
      this.validateAll()
      if (this.hasErrors) return

      try {
        let service
        let vals = {}
        if (!this.isEdit) vals.serviceId = this.serviceIdInput
        vals.label = this.label
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
  },
}
</script>

