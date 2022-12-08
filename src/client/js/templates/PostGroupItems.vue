<template>
<div>
  <div v-if="group">
    <h1 class="title">{{ group.label }}</h1>
    <p class="subtitle is-5">ServiceID: {{ serviceId }}</p>
  </div>

  <ul v-if="posts.length > 0" class="mt-6">
    <li
      v-for="post in posts"
      class="block"
    >
      <post-list-item
        :post="post"
      ></post-list-item>
    </li>
  </ul>

  <div v-else>
    <p>{{ $t('msg["Data is empty"]') }}</p>
  </div>
</div>
</template>
<script>
import { Post } from '@/api'
import PostListItem from '@/components/organisms/PostListItem'

export default{
  name: 'PostTags',

  components: {
    PostListItem,
  },

  data(){
    return {
      group: null,
    }
  },

  computed: {
    slug() {
      return this.$route.params.slug
    },

    posts() {
      if (this.checkEmpty(this.group) === true) return []
      return this.group.posts
    },
  },

  watch: {
    async slug(val) {
      await this.setPostGroup()
    },
  },

  async created() {
    await this.setPostGroup()
  },

  methods: {
    async setPostGroup() {
      if (!this.serviceId) return
      this.$store.dispatch('setLoading', true)
      try {
        const params = { withPostDetail:1 }
        this.group = await Post.getGroups(this.serviceId, this.slug, params)
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        console.log(err);//!!!!!!
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },
  }
}
</script>

