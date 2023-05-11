<template>
  <div>
    <div v-if="isEditModeActive">
      <category-select-recursive
        v-model="categorySlug"
        parent-category-slug="root"
      ></category-select-recursive>
      <div v-if="isEnabledUndo === true && defaultCategorySlug">
        <a
          @click="updateCategoryEditMode(false)"
          class="u-clickable"
        >{{ $t('common.undo') }}</a>
      </div>
    </div>
    <div v-else>
      <span>{{ inputtedCategoryLabel }}</span>
      <span>
        <a
          @click="updateCategoryEditMode(true)"
          class="ml-4 u-clickable"
        >{{ $t('common.edit') }}</a>
      </span>
    </div>
  </div>
</template>
<script>
import obj from '@/util/obj'
import { Category } from '@/api'
import CategorySelectRecursive from '@/components/molecules/CategorySelectRecursive'

export default{
  name: 'CategorySelect',

  components: {
    CategorySelectRecursive,
  },

  props: {
    // categorySlug
    value: {
      type: String,
      default: '',
    },

    isEnabledUndo: {
      type: Boolean,
      default: true,
    },
  },

  data(){
    return {
      categorySlug: '',
      defaultCategorySlug: '',
      isEditModeActive: false,
      inputtedCategory: null,
    }
  },

  computed: {
    inputtedCategoryLabel() {
      if (this.checkEmpty(this.inputtedCategory) === true) return ''
      if (obj.checkObjHasProp(this.inputtedCategory, 'parents') === false) {
        return this.inputtedCategory.label
      }

      let items = []
      this.inputtedCategory.parents.map((cate) => {
        items.push(cate.label)
      })
      items.push(this.inputtedCategory.label)
      return items.join(' > ')
    },
  },

  watch: {
    categorySlug(val) {
      this.$emit('input', val)
    },

    async value(val) {
      this.categorySlug = val
      if (val) {
        this.defaultCategorySlug = val
        await this.setCategory()
      }
      if (!this.categorySlug) {
        this.isEditModeActive = true
      } else {
        this.isEditModeActive = false
      }
    },
  },

  async created() {
    if (this.value) {
      this.defaultCategorySlug = this.value
      await this.setCategory()
    }
    if (!this.defaultCategorySlug || !this.inputtedCategory) this.isEditModeActive = true
  },

  methods: {
    async setCategory() {
      this.$store.dispatch('setLoading', true)
      try {
        this.inputtedCategory = await Category.get(this.serviceId, this.defaultCategorySlug, { withParents: 1 })
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        //this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
      }
    },

    updateCategoryEditMode(isActive) {
      if (isActive) {
        this.$emit('input', '')
        this.isEditModeActive = true
      } else {
        this.$emit('input', this.defaultCategorySlug)
        this.isEditModeActive = this.defaultCategorySlug ? false : true
      }
    },
  },
}
</script>

