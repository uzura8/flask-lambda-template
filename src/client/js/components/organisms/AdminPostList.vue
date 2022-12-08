<template>
<div>
  <div v-if="posts.length > 0">
    <table class="table is-fullwidth">
      <thead>
        <tr>
          <th class="is-size-7">{{ $t('common.status') }}</th>
          <th class="is-size-6">{{ $t('form.title') }}</th>
          <th class="is-size-6">{{ $t('common.category') }}</th>
          <th class="is-size-7">{{ $t('common.edit') }}</th>
          <th class="is-size-6">{{ $t('common.publishAt') }}</th>
          <th class="is-size-6">{{ $t('common.lastUpdatedAt') }}</th>
        </tr>
      </thead>
      <tfoot>
        <tr>
          <th class="is-size-7">{{ $t('common.status') }}</th>
          <th class="is-size-6">{{ $t('form.title') }}</th>
          <th class="is-size-6">{{ $t('common.category') }}</th>
          <th class="is-size-7">{{ $t('common.edit') }}</th>
          <th class="is-size-6">{{ $t('common.publishAt') }}</th>
          <th class="is-size-6">{{ $t('common.lastUpdatedAt') }}</th>
        </tr>
      </tfoot>
      <tbody>
        <admin-posts-table-row
          v-for="post in posts"
          :key="post.slug"
          :post="post"
        ></admin-posts-table-row>
      </tbody>
    </table>

    <nav class="pagination" role="navigation" aria-label="pagination">
      <router-link
        :to="`/admin/posts/${serviceId}?index=` + String(index - 1)"
        class="pagination-previous"
        :class="{'is-disabled': !existsPrev}"
      >
        <span class="icon">
          <i class="fas fa-angle-left"></i>
        </span>
        <span>{{ $t('common.toPrev') }}</span>
      </router-link>

      <router-link
        :to="`/admin/posts/${serviceId}?index=` + String(index + 1)"
        class="pagination-next"
        :class="{'is-disabled': !existsNext}"
      >
        <span class="icon">
          <i class="fas fa-angle-right"></i>
        </span>
        <span>{{ $t('common.toNext') }}</span>
      </router-link>

      <ul class="pagination-list">
        <li>
          <router-link
            :to="`/admin/posts/${serviceId}`"
            class="pagination-link"
            :class="{'is-disabled': !existsPrev}"
          >
            <span class="icon">
              <i class="fas fa-angle-double-left"></i>
            </span>
            <span>{{ $t('common.toFirst') }}</span>
          </router-link>
        </li>
      </ul>

    </nav>
  </div>
  <div v-else>
    <p>{{ $t('msg["Data is empty"]') }}</p>
  </div>
</div>
</template>
<script>
import { Admin } from '@/api'
import AdminPostsTableRow from '@/components/organisms/AdminPostsTableRow'

export default{
  name: 'AdminPostList',

  components: {
    AdminPostsTableRow,
  },

  props: {
  },

  data(){
    return {
      posts: [],
    }
  },

  computed: {
    index() {
      return this.$route.query.index ? Number(this.$route.query.index) : 0
    },

    currentPagerKey() {
      const current = this.$store.state.adminPostsPager.keys.find(item => item.index === this.index)
      return current ? current.key : null
    },

    existsNext() {
      const nextPage = this.index + 1
      return Boolean(this.$store.state.adminPostsPager.keys.find(item => item.index === nextPage))
    },

    existsPrev() {
      const prevPage = this.index - 1
      return prevPage >= 0
    },
  },

  watch: {
     index(val) {
      this.checkPageIndex()
      this.posts = []
      this.fetchPosts()
    },
  },

  async created() {
    this.checkPageIndex()
    await this.fetchPosts()
  },

  methods: {
    checkPageIndex() {
      if (this.index > this.$store.getters.adminPostsPagerIndexCount()) {
        this.$store.dispatch('resetAdminPostsPager', true)
        this.$router.push(`/admin/posts/${this.serviceId}`)
      }
    },

    async fetchPosts() {
      this.$store.dispatch('setLoading', true)
      try {
        let params = {}
        if (this.currentPagerKey) {
          params.lastKey = JSON.stringify(this.currentPagerKey)
        }
        const res = await Admin.getPosts(this.serviceId, null, params, this.adminUserToken)
        this.posts = res.items
        this.$store.dispatch('setAdminPostsPagerLastIndex', this.index)
        if (res.lastKey) {
          const item = {index: this.index + 1, key: res.lastKey}
          this.$store.dispatch('pushItemToAdminPostsPagerKeys', item)
        }
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        console.log(err)
        this.handleApiError(err, 'Failed to get data from server')
        this.$store.dispatch('setLoading', false)
      }
    },
  },
}
</script>

