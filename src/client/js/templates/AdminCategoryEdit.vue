<template>
<div>
  <h1 class="title">{{ $t('common.editOf', {label: $t('common.category')}) }}</h1>
  <admin-category-form
    v-if="category != null"
    :category="category"
  ></admin-category-form>
</div>
</template>
<script>
import { Category } from '@/api'
import AdminCategoryForm from '@/components/organisms/AdminCategoryForm'

export default{
  name: 'AdminCategoryEdit',

  components: {
    AdminCategoryForm,
  },

  data(){
    return {
      category: null,
    }
  },

  computed: {
    slug() {
      return this.$route.params.slug
    },
  },

  async created() {
    await this.setCategory()
  },

  methods: {
    async setCategory() {
      this.$store.dispatch('setLoading', true)
      try {
        this.$store.dispatch('setLoading', false)
        this.category = await Category.get(this.serviceId, this.slug, { withParents: 1 })
      } catch (err) {
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },
  },
}
</script>

