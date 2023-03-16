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
import CategorySelectRecursive from '@/components/molecules/category-select-recursive'

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
      this.$store.dispatch('setLoading', true)
      try {
        this.categories.splice(0, this.categories.length);
        const items = await Category.getChildren(this.serviceId, parentCateSlug)
        items.map((item) => {
          this.categories.push(item)
        })
        if (this.checkEmpty(items)) this.isHide = true
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        console.log(err);//!!!!!!
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },
  },
}
</script>

