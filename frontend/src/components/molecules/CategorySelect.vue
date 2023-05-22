<template>
  <div>
    <div v-if="isEditModeActive">
      <category-select-recursive
        v-model="categorySlug"
        parent-category-slug="root"
      ></category-select-recursive>
      <div v-if="isEnabledUndo === true && initialCategorySlug">
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
    // v-model value set from parent
    value: {
      type: String,
      default: '',
    },

    // is list loaded on parent
    isListLoaded: {
      type: Boolean,
      default: false,
    },

    isEnabledUndo: {
      type: Boolean,
      default: true,
    },
  },

  data(){
    return {
      categorySlug: '', // category value for handle
      initialCategorySlug: '',// to use reset to initial value
      isEditModeActive: true,// if true, display select field
      inputtedCategory: null, // if set value on parent, set category object
    }
  },

  computed: {
    inputtedCategoryLabel() {
      if (this.checkEmpty(this.inputtedCategory) === true) return ''
      if (obj.checkObjHasProp(this.inputtedCategory, 'parents') === false) {
        return this.inputtedCategory.label
      }

      // set parent categories
      let items = []
      this.inputtedCategory.parents.map((cate) => {
        items.push(cate.label)
      })
      items.push(this.inputtedCategory.label)
      return items.join(' > ')
    },
  },

  watch: {
    categorySlug(val, oldVal) {
      // emit to parent on changed at child components
      this.$emit('input', val)
    },

    isListLoaded(val) {
      // is parent list loaded
      if (val === true) {
        if (this.categorySlug) {
          // if set value, edit mode off
          this.isEditModeActive = false
        } else {
          // if set no value, edit mode on
          this.isEditModeActive = true
        }
      }
    },

    async value(val, oldVal) {
      // changed value on parent
      this.categorySlug = val
      if (val) {
        // if set value on parent, set category object
        this.initialCategorySlug = val
        await this.setInputtedCategory()
      } else {
        // if set no value on parent, edit mode on
        this.isEditModeActive = true
      }
    },
  },

  async created() {
    this.categorySlug = this.value

    // set value on parent
    if (this.value) {
      // reset to initial value
      this.initialCategorySlug = this.value
      // if set value on parent, set category object
      await this.setInputtedCategory()
    }
    if (this.value) {
        // if set value on parent, edit mode off
       this.isEditModeActive = false
    } else {
        // if set no value on parent, edit mode on
       this.isEditModeActive = true
    }
  },

  methods: {
    async setInputtedCategory() {
      this.$store.dispatch('setLoading', true)
      try {
        this.inputtedCategory = await Category.get(this.serviceId, this.initialCategorySlug, { withParents: 1 })
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        //this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
      }
    },

    updateCategoryEditMode(isActive) {
      if (isActive) {
        // on edit mode
        this.categorySlug = ''
        this.isEditModeActive = true
      } else {
        // reset to initial value
        this.categorySlug = this.initialCategorySlug
        // if initial value not set, edit mode on
        this.isEditModeActive = this.initialCategorySlug ? false : true
      }
    },
  },
}
</script>

