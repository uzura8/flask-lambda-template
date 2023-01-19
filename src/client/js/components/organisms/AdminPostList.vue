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
          <th
            @click="updateSortOrder('publishAt')"
            class="is-size-7 u-clickable is-underlined"
          >
            <span>{{ $t('common.publishAt') }}</span>
            <span
              v-if="publishAtSortIconClass"
              class="icon"
            >
              <i :class="publishAtSortIconClass"></i>
            </span>
          </th>
          <th
            @click="updateSortOrder('createdAt')"
            class="is-size-7 u-clickable is-underlined"
          >
            <span>{{ $t('common.createdAt') }}</span>
            <span
              v-if="createdAtSortIconClass"
              class="icon"
            >
              <i :class="createdAtSortIconClass"></i>
            </span>
          </th>
          <th class="is-size-7">{{ $t('common.lastUpdatedAt') }}</th>
        </tr>
      </thead>
      <tfoot>
        <tr>
          <th class="is-size-7">{{ $t('common.status') }}</th>
          <th class="is-size-6">{{ $t('form.title') }}</th>
          <th class="is-size-6">{{ $t('common.category') }}</th>
          <th class="is-size-7">{{ $t('common.edit') }}</th>
          <th
            @click="updateSortOrder('publishAt')"
            class="is-size-7 u-clickable is-underlined"
          >
            <span>{{ $t('common.publishAt') }}</span>
            <span
              v-if="publishAtSortIconClass"
              class="icon"
            >
              <i :class="publishAtSortIconClass"></i>
            </span>
          </th>
          <th
            @click="updateSortOrder('createdAt')"
            class="is-size-7 u-clickable is-underlined"
          >
            <span>{{ $t('common.createdAt') }}</span>
            <span
              v-if="createdAtSortIconClass"
              class="icon"
            >
              <i :class="createdAtSortIconClass"></i>
            </span>
          </th>
          <th class="is-size-7">{{ $t('common.lastUpdatedAt') }}</th>
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
        :to="{ path:`/admin/posts/${serviceId}`, query:{sort:sort, order:order, index:String(index - 1)}}"
        class="pagination-previous"
        :class="{'is-disabled': !existsPrev}"
      >
        <span class="icon">
          <i class="fas fa-angle-left"></i>
        </span>
        <span>{{ $t('common.toPrev') }}</span>
      </router-link>

      <router-link
        :to="{ path:`/admin/posts/${serviceId}`, query:{sort:sort, order:order, index:String(index + 1)}}"
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
            :to="{ path:`/admin/posts/${serviceId}`, query:{sort:sort, order:order}}"
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

    sort() {
      const defaultValue = 'createdAt'
      if (!this.$route.query.sort) return defaultValue
      return this.$route.query.sort
    },

    order() {
      const defaultValue = 'desc'
      if (!this.$route.query.order) return defaultValue
      return this.$route.query.order
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

    createdAtSortIconClass() {
      if (this.sort !== 'createdAt') return ''
      const classSuffix = this.order === 'asc' ? 'up' : 'down'
      return `fas fa-caret-${classSuffix}`
    },

    publishAtSortIconClass() {
      if (this.sort !== 'publishAt') return ''
      const classSuffix = this.order === 'asc' ? 'up' : 'down'
      return `fas fa-caret-${classSuffix}`
    },
  },

  watch: {
    index(val) {
      this.fetchPosts()
    },

    sort(val) {
      this.$store.dispatch('resetAdminPostsPager', true)
      this.fetchPosts()
    },

    order(val) {
      this.$store.dispatch('resetAdminPostsPager', true)
      this.fetchPosts()
    },
  },

  async created() {
    await this.fetchPosts()
  },

  methods: {
    updateSortOrder(sortKey) {
      let order = 'desc'
      if (this.sort === sortKey) {
        order = this.order === 'asc' ? 'desc' : 'asc'
      }
      this.$router.push({ query:{ sort:sortKey, order:order } })
    },

    async fetchPosts() {
      this.validateQueries()
      this.$store.dispatch('setLoading', true)
      try {
        let params = {
          sort: this.sort,
          order: this.order,
        }
        let params_clone = {...params}
        if (this.currentPagerKey) {
          params.pagerKey = JSON.stringify(this.currentPagerKey)
        }
        const res = await Admin.getPosts(this.serviceId, null, params, this.adminUserToken)
        this.posts = res.items
        params_clone.index = this.index
        this.$store.dispatch('setAdminPostsPagerParams', params_clone)
        if (res.pagerKey) {
          const nextPagerKey = {index: this.index + 1, key: res.pagerKey}
          this.$store.dispatch('pushItemToAdminPostsPagerKeys', nextPagerKey)
        }
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        console.log(err)
        this.handleApiError(err, 'Failed to get data from server')
        this.$store.dispatch('setLoading', false)
      }
    },

    validateQueries() {
      if (this.validateIndex() === false
        || this.validateSort() === false
        || this.validateOrder() === false) {
        this.$store.dispatch('resetAdminPostsPager', true)
        this.$router.push(`/admin/posts/${this.serviceId}`)
      }
    },

    validateIndex() {
      if (this.index > this.$store.getters.adminPostsPagerIndexCount()) return false
      if (this.index < 0) return false
      return true
    },

    validateSort() {
      return ['createdAt', 'publishAt'].includes(this.sort)
    },

    validateOrder() {
      return ['asc', 'desc'].includes(this.order)
    },
  },
}
</script>

