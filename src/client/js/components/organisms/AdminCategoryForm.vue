<template>
<div>
  <b-field
    :label="$t('common.parentCategory')"
    :type="checkEmpty(errors.parentCategorySlug) ? '' : 'is-danger'"
    :message="checkEmpty(errors.parentCategorySlug) ? '' : errors.parentCategorySlug[0]"
    class="mt-5"
  >
    <category-select
      v-model="parentCategorySlug"
    ></category-select>
  </b-field>

  <b-field
    :label="$t('form.slug')"
    :type="checkEmpty(errors.slug) ? '' : 'is-danger'"
    :message="checkEmpty(errors.slug) ? '' : errors.slug[0]"
    class="mt-5"
  >
    <div v-if="isEdit">
      {{ category.slug }}
    </div>
    <b-input
      v-else
      v-model="slug"
      @blur="validate('slug')"
    ></b-input>
  </b-field>

  <b-field
    :label="$t('form.label')"
    :type="checkEmpty(errors.label) ? '' : 'is-danger'"
    :message="checkEmpty(errors.label) ? '' : errors.label[0]"
    class="mt-5"
  >
    <b-input
      v-model="label"
      @blur="validate('label')"
    ></b-input>
  </b-field>

  <div class="field mt-5">
    <div class="control">
      <button
        class="button is-info"
        :disabled="isLoading || hasErrors"
        @click="save(true)"
        v-text="isEdit ? $t('common.edit') : $t('common.add')"
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
import obj from '@/util/obj'
import { Category, Admin } from '@/api'
import CategorySelect from '@/components/molecules/CategorySelect'

export default {
  name: 'AdminCategoryForm',

  components: {
    CategorySelect,
  },

  props: {
    category: {
      type: Object,
      required: false,
      default: null,
    },

    parentCategorySlugDefault: {
      type: String,
      required: false,
      default: '',
    },
  },

  data() {
    return {
      slug: '',
      label: '',
      parentCategorySlug: '',
      fieldKeys: ['slug', 'label', 'parentCategorySlug'],
      //queryParentCate: null,
    }
  },

  computed: {
    isEdit() {
      return this.category != null
    },

    isEmptyRequiredFields() {
      if (!this.checkEmpty(this.slug)) return false
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

  watch: {
    parentCategorySlug(val) {
      this.initError('parentCategorySlug')
    },
  },

  async created() {
    if (this.isEdit === true) {
      this.setCategory()
    } else {
      if (this.parentCategorySlugDefault) {
        this.parentCategorySlug = this.parentCategorySlugDefault
      }
    }
  },

  methods: {
    setCategory() {
      this.slug = this.category.slug != null ? String(this.category.slug) : ''
      this.label = this.category.label != null ? String(this.category.label) : ''
      if (obj.checkObjHasProp(this.category, 'parents', true)) {
        let parents = this.category.parents
        parents.sort((a, b) => {
          if (a.parentPath < b.parentPath) {
            return -1
          }
          if (a.parentPath > b.parentPath) {
            return 1
          }
          return 0
        })
        const parentCate = parents.slice(-1)[0]
        this.parentCategorySlug = parentCate.slug
      }
    },

    resetInputs() {
      this.slug = ''
      this.label = ''
    },

    async save() {
      this.validateAll()
      if (this.hasErrors) return

      try {
        let vals = {}
        vals.label = this.label
        vals.parentCategorySlug = this.parentCategorySlug
        if (this.isEdit === false) vals.slug = this.slug

        this.$store.dispatch('setLoading', true)
        let res
        if (this.isEdit) {
          res = await Admin.updateCategory(this.serviceId, this.slug, vals, this.adminUserToken)
        } else {
          res = await Admin.createCategory(this.serviceId, vals, this.adminUserToken)
        }
        this.$store.dispatch('setLoading', false)
        this.$emit('posted', res)
        this.resetInputs()
        this.$router.push(`/admin/categories/${this.serviceId}`)
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
      this.$router.push(`/admin/categories/${this.serviceId}`)
    },

    async checkSlugNotExists(slug) {
      try {
        this.$store.dispatch('setLoading', true)
        const res = await Admin.checkCategorySlugNotExists(this.serviceId, slug, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
        return res
      } catch (err) {
        console.log(err);//!!!!!!
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err)
      }
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

    async validateSlug() {
      this.initError('slug')
      if (this.slug === null) this.slug = ''
      this.slug = this.slug.trim()
      if (this.checkEmpty(this.slug)) {
        this.errors.slug.push(this.$t('msg["Input required"]'))
      } else if (str.checkSlug(this.slug) === false) {
        this.errors.slug.push(this.$t('msg.InvalidInput'))
      } else if (this.isEdit === false || this.slug !== this.category.slug) {
        const isNotExists = await this.checkSlugNotExists(this.slug)
        if (isNotExists === false) {
          this.errors.slug.push(this.$t('msg["Already in use"]'))
        }
      }
    },

    async validateParentCategorySlug() {
      this.initError('parentCategorySlug')
      if (this.parentCategorySlug === null) this.parentCategorySlug = ''
      this.parentCategorySlug = this.parentCategorySlug.trim()
      if (!this.checkEmpty(this.parentCategorySlug) && str.checkSlug(this.parentCategorySlug) === false) {
        this.errors.parentCategorySlug.push(this.$t('msg.InvalidInput'))
      } else if (this.parentCategorySlug === this.slug) {
        this.errors.parentCategorySlug.push(this.$t('msg.inputDifferentValueFrom', {target: this.$t('form.slug')}))
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
