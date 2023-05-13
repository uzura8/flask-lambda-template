<template>
<div>
  <ul v-if="posts.length > 0">
    <li
      v-for="post in posts"
      class="block"
    >
      <post-list-item-for-select
        v-if="['simple', 'simpleSelect'].includes(listType)"
        :post="post"
        :select-disabled="selectedIds.includes(post.postId)"
        @select="selectPost"
        class="mt-3"
      ></post-list-item-for-select>

      <post-list-item
        v-else-if="listType === 'normal'"
        :post="post"
      ></post-list-item>
    </li>
  </ul>

  <div v-else-if="isLoading === false">
    <p>{{ $t('msg["Data is empty"]') }}</p>
  </div>

  <nav v-if="hasNext" class="u-mt2r">
    <a class="u-clickable" @click="fetchPosts()">{{ $t('common.more') }}</a>
  </nav>
</div>
</template>
<script>
import { Post } from '@/api'
import PostListItem from '@/components/organisms/PostListItem'
import PostListItemForSelect from '@/components/organisms/PostListItemForSelect'

export default{
  name: 'PostList',

  components: {
    PostListItem,
    PostListItemForSelect,
  },

  props: {
    listType: {
      type: String,
      default: 'normal',
      validator (val) {
        return ['normal', 'simple', 'simpleSelect'].includes(val)
      },
    },

    selectedIds: {
      type: Array,
      default: () => ([]),
    },
  },

  data(){
    return {
      posts: [],
      pagerKey: null,
      listCount: 10,
    }
  },

  computed: {
    categorySlug() {
      return this.$route.params.categorySlug
    },

    tagLabel() {
      return this.$route.params.tagLabel
    },

    hasNext() {
      return this.pagerKey != null
    },
  },

  watch: {
    categorySlug() {
      this.resetPosts()
      this.fetchPosts()
    },

    tagLabel() {
      this.resetPosts()
      this.fetchPosts()
    },
  },

  async created() {
    await this.fetchPosts()
  },

  methods: {
    resetPosts() {
      this.pagerKey= null
      this.posts = []
    },

    async fetchPosts(isLatest = false) {
      let params = {}
      if (this.pagerKey != null) {
        params.pagerKey = JSON.stringify(this.pagerKey)
      }
      params.count = this.listCount

      if (this.categorySlug) {
        params.category = this.categorySlug
      } else if (this.tagLabel) {
        params.tag = this.tagLabel
      }

      this.$store.dispatch('setLoading', true)
      try {
        const res = await Post.get(this.serviceId, null, params)
        this.pagerKey = res.pagerKey
        let items = res.items
        if (isLatest) {
          items.reverse()
        }
        items.map(item => {
          if (isLatest) {
            this.posts.unshift(item)
          } else {
            this.posts.push(item)
          }
        })
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    selectPost(post) {
      this.$emit('select', post)
    },
  },
}
</script>

