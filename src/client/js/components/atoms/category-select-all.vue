<template>
<b-select
  v-model="cateSlug"
  :placeholder="$t('msg.pleaseSelect')"
  @input="updateValue"
>
  <option
    v-for="cate in categories"
    :key="cate.slug"
    :value="cate.slug"
  >{{ cate.label }}</option>
</b-select>
</template>
<script>
import { Category } from '@/api'

export default{
  name: 'CategorySelectAll',

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
    }
  },

  computed: {
  },

  watch: {
  },

  async created() {
    await this.setCategories(this.parentCategorySlug)
  },

  methods: {
    updateValue(newValue) {
      this.$emit('input', newValue)
    },

    async setCategories(parentCateSlug) {
      try {
        this.categories.splice(0, this.categories.length);
        const items = await Category.getChildren(this.serviceId, parentCateSlug)
        items.map((item) => {
          this.categories.push(item)
        })
        if (this.checkEmpty(items)) this.isHide = true
      } catch (err) {
        console.log(err);//!!!!!!
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },
  },
}
</script>

