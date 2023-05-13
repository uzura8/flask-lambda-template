<template>
<div class="field is-grouped is-grouped-multiline">
  <b-select
    v-if="isHide === false"
    v-model="cateSlug"
    :placeholder="$t('msg.pleaseSelect')"
    @input="updateValue($event, parentCategorySlug)"
  >
    <option
      v-if="isLoading === false"
      value=""
    >{{ $t('msg.pleaseSelect') }}</option>
    <option
      v-for="cate in categories"
      :key="cate.slug"
      :value="cate.slug"
    >{{ cate.label }}</option>
  </b-select>

  <b-loading
    v-model="isLoadingLocal"
    :is-full-page="false"
  ></b-loading>

  <category-select-recursive
    v-if="cateSlug"
    v-model="inputtedValue"
    :parent-category-slug="cateSlug"
    @input="updateValue($event, cateSlug)"
  ></category-select-recursive>
</div>
</template>
<script>
import { Category } from '@/api'
import CategorySelectRecursive from '@/components/molecules/CategorySelectRecursive'

export default{
  name: 'CategorySelectRecursive',

  components: {
    CategorySelectRecursive,
  },

  props: {
    parentCategorySlug: {
      type: String,
      required: true,
    },

    value: {
      type: String,
      default: '',
    },
  },

  data(){
    return {
      cateSlug: '',
      categories: [],
      isHide: false,
      isLoadingLocal: false,
    }
  },

  computed: {
    inputtedValue: {
      get() {
        return this.value
      },
      set(newValue) {
        this.$emit('input', newValue)
      },
    },
  },

  watch: {
    async parentCategorySlug(val, oldVal) {
      if (!oldVal) return
      await this.setCategories(val)
    },

    value(val) {
      if (!val) this.cateSlug = ''
    },
  },

  async created() {
    await this.setCategories(this.parentCategorySlug)
  },

  methods: {
    updateValue(newValue, parentCate) {
      let val = newValue ? newValue : parentCate
      if (val === 'root') val = ''
      this.$emit('input', val)
    },

    async setCategories(parentCateSlug) {
      this.isLoadingLocal = true
      try {
        this.categories.splice(0, this.categories.length)
        const items = await Category.getChildren(this.serviceId, parentCateSlug)
        items.map((item) => {
          this.categories.push(item)
        })
        if (this.checkEmpty(items)) this.isHide = true
        this.isLoadingLocal = false
      } catch (err) {
        //this.debugOutput(err)
        this.isLoadingLocal = false
        //this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },
  },
}
</script>

