<template>
<div>
  <div v-if="category">
    <h1 class="title">{{ $t('common.postsOf', {label: category.label}) }}</h1>
    <p class="subtitle is-5">ServiceID: {{ serviceId }}</p>
  </div>
  <post-list class="mt-6"></post-list>
</div>
</template>
<script>
import { Category } from '@/api'
import PostList from '@/components/organisms/PostList'

export default{
  name: 'PostCategories',

  components: {
    PostList,
  },

  data() {
    return {
      category: null,
    }
  },

  computed: {
    categorySlug() {
      return this.$route.params.categorySlug
    },
  },

  watch: {
    categorySlug(val) {
      this.fetchCategory(val)
    },
  },

  async created() {
    await this.fetchCategory(this.categorySlug)
  },

  methods: {
    async fetchCategory(categorySlug) {
      this.$store.dispatch('setLoading', true)
      try {
        this.category = await Category.get(this.serviceId, categorySlug)
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },
  },
}
</script>

