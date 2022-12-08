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

  <div v-else>
    <p>{{ $t('msg["Data is empty"]') }}</p>
  </div>

  <nav v-if="hasNext" class="u-mt2r">
    <a class="u-clickable" @click="fetchPosts({ untilTime:lastItemPublishedAt })">{{ $t('common.more') }}</a>
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
      hasNext: false,
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

    lastItemPublishedAt () {
      const lastIndex = this.posts.length - 1
      return this.posts.length > 0 ? encodeURI(this.posts[lastIndex].publishAt) : null
    },
  },

  watch: {
    categorySlug() {
      this.posts = []
      this.fetchPosts()
    },

    tagLabel() {
      this.posts = []
      this.fetchPosts()
    },
  },

  async created() {
    await this.fetchPosts()
  },

  methods: {
    async fetchPosts(params = {}, isLatest = false) {
      const params_copied = { ...params }
      params_copied.count = this.listCount + 1

      if (this.categorySlug) {
        params_copied.category = this.categorySlug
      } else if (this.tagLabel) {
        params_copied.tag = this.tagLabel
      }

      this.$store.dispatch('setLoading', true)
      try {
        let items = await Post.get(this.serviceId, null, params_copied)
        if (isLatest) {
          items.reverse()
        } else {
          if (items.length > this.listCount) {
            items.pop()
            this.hasNext = true
          } else {
            this.hasNext = false
          }
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
        console.log(err);//!!!!!!
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

