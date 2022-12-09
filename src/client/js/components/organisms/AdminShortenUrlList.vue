<template>
<div>
  <div v-if="shortenUrls.length > 0">
    <table class="table is-fullwidth">
      <thead>
        <tr>
          <th class="is-size-6">ID</th>
          <th class="is-size-6">{{ $t('common.name') }}</th>
          <th class="is-size-6">{{ $t('common.url') }}</th>
          <th class="is-size-7">{{ $t('common.via') }}</th>
          <th class="is-size-7">{{ $t('common.edit') }}</th>
          <th class="is-size-6">{{ $t('common.createdAt') }}</th>
        </tr>
      </thead>
      <tfoot>
        <tr>
          <th class="is-size-6">ID</th>
          <th class="is-size-6">{{ $t('common.name') }}</th>
          <th class="is-size-6">{{ $t('common.url') }}</th>
          <th class="is-size-7">{{ $t('common.via') }}</th>
          <th class="is-size-7">{{ $t('common.edit') }}</th>
          <th class="is-size-6">{{ $t('common.createdAt') }}</th>
        </tr>
      </tfoot>
      <tbody>
        <admin-shorten-urls-table-row
          v-for="shortenUrl in shortenUrls"
          :key="shortenUrl.urlId"
          :shorten-url="shortenUrl"
        ></admin-shorten-urls-table-row>
      </tbody>
    </table>

    <nav class="pagination" role="navigation" aria-label="pagination">
      <router-link
        :to="`/admin/shorten-urls/${serviceId}?index=` + String(index - 1)"
        class="pagination-previous"
        :class="{'is-disabled': !existsPrev}"
      >
        <span class="icon">
          <i class="fas fa-angle-left"></i>
        </span>
        <span>{{ $t('common.toPrev') }}</span>
      </router-link>

      <router-link
        :to="`/admin/shorten-urls/${serviceId}?index=` + String(index + 1)"
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
            :to="`/admin/shorten-urls/${serviceId}`"
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
  <div v-else-if="isLoading === false">
    <p>{{ $t('msg["Data is empty"]') }}</p>
  </div>
</div>
</template>
<script>
import { Admin } from '@/api'
import AdminShortenUrlsTableRow from '@/components/organisms/AdminShortenUrlsTableRow'

export default{
  name: 'AdminShortenUrlList',

  components: {
    AdminShortenUrlsTableRow,
  },

  props: {
  },

  data(){
    return {
      shortenUrls: [],
    }
  },

  computed: {
    index() {
      return this.$route.query.index ? Number(this.$route.query.index) : 0
    },

    currentPagerKey() {
      const current = this.$store.state.adminShortenUrlsPager.keys.find(item => item.index === this.index)
      return current ? current.key : null
    },

    existsNext() {
      const nextPage = this.index + 1
      return Boolean(this.$store.state.adminShortenUrlsPager.keys.find(item => item.index === nextPage))
    },

    existsPrev() {
      const prevPage = this.index - 1
      return prevPage >= 0
    },
  },

  watch: {
     index(val) {
      this.checkPageIndex()
      this.shortenUrls = []
      this.fetchShortenUrls()
    },
  },

  async created() {
    this.checkPageIndex()
    await this.fetchShortenUrls()
  },

  methods: {
    checkPageIndex() {
      if (this.index > this.$store.getters.adminShortenUrlsPagerIndexCount()) {
        this.$store.dispatch('resetAdminShortenUrlsPager', true)
        this.$router.push(`/admin/shorten-urls/${this.serviceId}`)
      }
    },

    async fetchShortenUrls() {
      this.$store.dispatch('setLoading', true)
      try {
        let params = {}
        if (this.currentPagerKey) {
          params.lastKey = JSON.stringify(this.currentPagerKey)
        }
        const res = await Admin.getShortenUrls(this.serviceId, null, params, this.adminUserToken)
        this.shortenUrls = res.items
        this.$store.dispatch('setAdminShortenUrlsPagerLastIndex', this.index)
        if (res.lastKey) {
          const item = {index: this.index + 1, key: res.lastKey}
          this.$store.dispatch('pushItemToAdminShortenUrlsPagerKeys', item)
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

