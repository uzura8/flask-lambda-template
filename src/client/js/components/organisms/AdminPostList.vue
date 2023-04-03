<template>
<div>

  <div class="card">
    <header
      class="card-header u-clickable"
      @click="isFilterActive = !isFilterActive"
    >
      <p class="card-header-title">
        {{ $t('form.specifyingFilterConditions') }}
      </p>
      <button
        class="card-header-icon"
        aria-label="more options"
      >
        <span class="icon">
          <i
            class="fas"
            :class="{'fa-angle-down':!isFilterActive, 'fa-angle-up':isFilterActive}"
            aria-hidden="true"
          ></i>
        </span>
      </button>
    </header>

    <div
      v-if="isFilterActive"
      class="card-content"
    >
      <div class="content">
        <b-field grouped>
          <b-field :label="$t('common.target')">
            <b-select v-model="filterAttribute">
              <option
                v-for="item in filterAttributeOptions"
                :value="item.value"
                v-text="$t(item.labelKey)"
              ></option>
            </b-select>
          </b-field>

          <b-field :label="$t('common.condition')">
            <b-select v-model="filterCompare">
              <option
                v-for="item in filterCompareOptions"
                :value="item.value"
                v-text="$t(item.labelKey)"
              ></option>
            </b-select>
          </b-field>

          <b-field :label="$t('common.value')" expanded>
            <b-input
              v-model="filterValue"
              @blur="validateFilterWithError()"
            ></b-input>
          </b-field>
        </b-field>

        <p
          v-if="filterInputError"
          class="has-text-danger"
        >{{ filterInputError }}</p>

        <b-field grouped>
          <b-field :label="$t('common.category')">
            <category-select
              v-model="filterCategory"
              :is-enabled-undo="false"
            ></category-select>
          </b-field>
        </b-field>

        <p
          v-if="filterCategoryInputError"
          class="has-text-danger"
        >{{ filterCategoryInputError }}</p>

        <b-field class="mt-4" grouped>
          <b-field>
            <button
              class="button is-info"
              @click="executeFilter()"
              :disabled="hasFilterInputError"
            >{{ $t('common.run') }}</button>
          </b-field>
          <b-field>
            <button
              class="button is-light"
              @click="resetFilter()"
            >{{ $t('common.reset') }}</button>
          </b-field>
        </b-field>
      </div>
    </div>
  </div>

  <div v-if="posts.length > 0">
    <table class="table is-fullwidth mt-6">
      <thead>
        <tr>
          <th class="is-size-7">{{ $t('common.status') }}</th>
          <th class="is-size-6">{{ $t('form.title') }}</th>
          <th class="is-size-7">{{ $t('common.category') }}</th>
          <th class="is-size-7">{{ $t('common.edit') }}</th>
          <th
            class="is-size-7 u-clickable is-underlined"
          >
            <router-link
              :to="getUrlObjBySortOrder('publishAt')"
            >
              <span>{{ $t('common.publishAt') }}</span>
              <span
                v-if="publishAtSortIconClass"
                class="icon"
              >
                <i :class="publishAtSortIconClass"></i>
              </span>
             </router-link>
          </th>
          <th
            class="is-size-7 u-clickable is-underlined"
          >
            <router-link
              :to="getUrlObjBySortOrder('createdAt')"
            >
              <span>{{ $t('common.createdAt') }}</span>
              <span
                v-if="createdAtSortIconClass"
                class="icon"
              >
                <i :class="createdAtSortIconClass"></i>
              </span>
             </router-link>
          </th>
          <th class="is-size-7">{{ $t('common.lastUpdatedAt') }}</th>
        </tr>
      </thead>
      <tfoot>
        <tr>
          <th class="is-size-7">{{ $t('common.status') }}</th>
          <th class="is-size-6">{{ $t('form.title') }}</th>
          <th class="is-size-7">{{ $t('common.category') }}</th>
          <th class="is-size-7">{{ $t('common.edit') }}</th>
          <th
            class="is-size-7 u-clickable is-underlined"
          >
            <router-link
              :to="getUrlObjBySortOrder('publishAt')"
            >
              <span>{{ $t('common.publishAt') }}</span>
              <span
                v-if="publishAtSortIconClass"
                class="icon"
              >
                <i :class="publishAtSortIconClass"></i>
              </span>
             </router-link>
          </th>
          <th
            class="is-size-7 u-clickable is-underlined"
          >
            <router-link
              :to="getUrlObjBySortOrder('createdAt')"
            >
              <span>{{ $t('common.createdAt') }}</span>
              <span
                v-if="createdAtSortIconClass"
                class="icon"
              >
                <i :class="createdAtSortIconClass"></i>
              </span>
             </router-link>
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
        :to="getUrlObjByPageIndex(index - 1)"
        class="pagination-previous"
        :class="{'is-disabled': !existsPrev}"
      >
        <span class="icon">
          <i class="fas fa-angle-left"></i>
        </span>
        <span>{{ $t('common.toPrev') }}</span>
      </router-link>

      <router-link
        :to="getUrlObjByPageIndex(index + 1)"
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
            :to="getUrlObjByPageIndex()"
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
    <p class="mt-6">{{ $t('msg["Data is empty"]') }}</p>
  </div>
</div>
</template>
<script>
import utilStr from '@/util/str'
import utilObj from '@/util/obj'
import { Admin, Category } from '@/api'
import AdminPostsTableRow from '@/components/organisms/AdminPostsTableRow'
import CategorySelect from '@/components/molecules/CategorySelect'

export default{
  name: 'AdminPostList',

  components: {
    AdminPostsTableRow,
    CategorySelect,
  },

  props: {
  },

  data(){
    return {
      posts: [],
      sortsAllowed: ['createdAt', 'publishAt'],
      ordersAllowed: ['asc', 'desc'],
      isFilterActive: false,
      filterAttribute: 'slug',
      filterCompare: 'eq',
      filterValue: '',
      filterAttributeOptions: [
        {labelKey:'form.slug', value:'slug'},
        {labelKey:'form.title', value:'title'},
        {labelKey:'form.body', value:'body'},
      ],
      filterCompareOptions: [
        {labelKey:'common.equalTo', value:'eq'},
        {labelKey:'common.contains', value:'contains'},
      ],
      filterInputError: '',
      filterCategory: '',
      filterCategoryInputError: '',
      requestedParams: {},
    }
  },

  computed: {
    index() {
      return this.$route.query.index ? Number(this.$route.query.index) : 0
    },

    sort() {
      const defaultValue = 'createdAt'
      const reqSort = this.$route.query.sort
      if (!reqSort) return defaultValue
      return reqSort
    },

    order() {
      const defaultValue = 'desc'
      const reqOrder = this.$route.query.order
      if (!reqOrder) return defaultValue
      return this.$route.query.order
    },

    filterCategoryQuery() {
      const defaultValue = ''
      if (!this.$route.query.category) return defaultValue
      return this.$route.query.category
    },

    filterCategoryInput() {
      const defaultValue = ''
      if (this.filterCategoryInputError) return defaultValue
      return this.filterCategory
    },

    filterCategoryForReq() {
      if (this.filterCategoryInput) return this.filterCategoryInput
      if (this.filterCategoryQuery) return this.filterCategoryQuery
      return ''
    },

    filtersQuery() {
      const defaultValue = null
      if (!this.$route.query.filters) return defaultValue
      if (utilStr.checkJson(this.$route.query.filters) === false) return defaultValue

      const reqFilters = JSON.parse(this.$route.query.filters)
      if (utilObj.checkObjItemsNotEmpty(reqFilters, ['value', 'attribute', 'compare'], true) === false) {
        return defaultValue
      }
      return reqFilters
    },

    filtersInput() {
      const defaultValue = null
      if (this.filterInputError) return defaultValue
      const inputs = {
        attribute: this.filterAttribute,
        compare: this.filterCompare,
        value: this.filterValue,
      }
      if (utilObj.checkObjItemsNotEmpty(inputs, ['value', 'attribute', 'compare'], true) === false) {
        return defaultValue
      }
      return inputs
    },

    filters() {
      if (this.checkEmpty(this.filtersInput) === false) return this.filtersInput
      if (this.checkEmpty(this.filtersQuery) === false) return this.filtersQuery
      return null
    },

    filtersJson() {
      const defaultValue = ''
      if (this.checkEmpty(this.filters) === true) return defaultValue
      if (utilObj.checkObjItemsNotEmpty(this.filters, ['value', 'attribute', 'compare'], true) === false) {
        return defaultValue
      }
      return JSON.stringify(this.filters)
    },

    currentPagerKey() {
      if (this.validateIndex() === false) return null
      const current = this.$store.state.adminPostsPager.keys.find(item => item.index === this.index)
      return current ? current.key : null
    },

    currentParams() {
      let params = {
        sort: this.sort,
        order: this.order,
      }
      if (this.filterCategory) {
        params.category = this.filterCategory
      }
      if (this.filters) {
        params.filters = this.filters
      }
      if (this.currentPagerKey) {
        params.pagerKey = this.currentPagerKey
      }
      return params
    },

    currentParamsForReq() {
      let params = {
        sort: this.sort,
        order: this.order,
      }
      if (this.filterCategory) {
        params.category = this.filterCategory
      }
      if (this.filters) {
        params.filters = JSON.stringify(this.filters)
      }
      if (this.currentPagerKey) {
        params.pagerKey = JSON.stringify(this.currentPagerKey)
      }
      return params
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

    hasFilterInputError() {
      if (this.filterInputError.length > 0) return true
      if (this.filterCategoryInputError.length > 0) return true
      return false
    },

    filterAttributesAllowed() {
      return this.filterAttributeOptions.map(item => item.value)
    },

    filterComparesAllowed() {
      return this.filterCompareOptions.map(item => item.value)
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
    this.checkReqIndexAndRedirect()

    await this.setCategories()
    if (this.filtersQuery) {
      this.filterAttribute = this.filtersQuery.attribute
      this.filterCompare = this.filtersQuery.compare
      this.filterValue = this.filtersQuery.value
      this.isFilterActive = true
    }
    if (this.filterCategoryQuery) {
      this.filterCategory = this.filterCategoryQuery
      this.isFilterActive = true
    }
    await this.fetchPosts()
  },

  methods: {
    checkReqIndexAndRedirect() {
      if (this.validateIndex() === false) {
        this.$store.dispatch('resetAdminPostsPager', true)
        this.$router.push({path: `/admin/posts/${this.serviceId}`, query: this.currentParamsForReq})
      }
    },

    updateSortOrder(sortKey) {
      let order = 'desc'
      if (this.sort === sortKey) {
        order = this.order === 'asc' ? 'desc' : 'asc'
      }

      let paramsCloned = { ...this.currentParamsForReq }
      paramsCloned.sort = sortKey
      paramsCloned.order = order
      this.$router.push({ query: paramsCloned })
    },

    getUrlObjBySortOrder(sortKey) {
      let order = 'desc'
      if (this.sort === sortKey) {
        order = this.order === 'asc' ? 'desc' : 'asc'
      }

      let paramsCloned = { ...this.currentParamsForReq }
      paramsCloned.sort = sortKey
      paramsCloned.order = order
      return {
        path:`/admin/posts/${this.serviceId}`,
        query: paramsCloned,
      }
    },

    getUrlObjByPageIndex(index=0) {
      let paramsCloned = { ...this.currentParamsForReq }
      paramsCloned.index = String(index)
      return {
        path:`/admin/posts/${this.serviceId}`,
        query: paramsCloned,
      }
    },

    async executeFilter() {
      this.validateFilterWithError()
      if (this.hasFilterInputError) return
      if (this.checkUpdatedReqParams(this.currentParamsForReq) === false) return

      this.$store.dispatch('resetAdminPostsPager', true)
      this.$router.push({ query:this.currentParamsForReq })
      await this.fetchPosts()
    },

    async resetFilter() {
      this.filterAttribute = 'slug'
      this.filterCompare = 'eq'
      this.filterValue = ''
      this.filterInputError = ''
      this.filterCategory = ''
      this.filterCategoryInputError = ''
      const params = {
        sort: this.sort,
        order: this.order,
      }
      if (this.checkUpdatedReqParams(params) === false) return

      this.$store.dispatch('resetAdminPostsPager', true)
      this.$router.push({ query: params })
      await this.fetchPosts(params)
    },

    async setCategories() {
      if (this.checkEmpty(this.$store.state.categoryItems) === false) return

      this.$store.dispatch('setLoading', true)
      try {
        const res = await Category.get(this.serviceId, null, { isList: 1 })
        this.$store.dispatch('setCategoryItems', res)
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        this.debugOutput(err)
        this.handleApiError(err, 'Failed to get data from server')
        this.$store.dispatch('setLoading', false)
      }
    },

    async fetchPosts(params = null) {
      if (this.validateAll() === false) {
        this.showGlobalMessage(this.$t('msg.InvalidInput'))
        return
      }

      if (params == null) {
        params = this.currentParamsForReq
      }
      let paramsForApi = { ...params }
      paramsForApi.withCategory = 0

      this.$store.dispatch('setLoading', true)
      try {
        const res = await Admin.getPosts(this.serviceId, null, paramsForApi, this.adminUserToken)
        this.posts = res.items
        this.setRequestedParams(params)

        let paramsForStore = {...this.currentParams}
        paramsForStore.index = this.index
        this.$store.dispatch('setAdminPostsPagerParams', paramsForStore)
        if (res.pagerKey) {
          const nextPagerKey = {index: this.index + 1, key: res.pagerKey}
          this.$store.dispatch('pushItemToAdminPostsPagerKeys', nextPagerKey)
        }
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        this.debugOutput(err)
        this.handleApiError(err, 'Failed to get data from server')
        this.$store.dispatch('setLoading', false)
      }
    },

    validateAll() {
      if (this.sortsAllowed.includes(this.sort) === false) return false
      if (this.ordersAllowed.includes(this.order) === false) return false
      if (this.validateFilterAttribute() === false) return false
      if (this.validateFilterCompare() === false) return false
      if (this.validateFilterValue() === false) return false
      return true
    },

    validateIndex() {
      if (this.index > this.$store.getters.adminPostsPagerIndexCount()) return false
      if (this.index < 0) return false
      return true
    },

    validateFilterWithError() {
      this.resetFilterError()
      if (this.validateFilterAttribute() === false || this.validateFilterCompare() === false) {
        this.filterInputError = this.$t('msg.InvalidInput')
      } else if (this.validateFilterValue() === false) {
        this.filterInputError = this.$t('msg.inputNoMoreThanTargetCharacters', {num: 30})
      } else if (this.validateFilterCategory() === false) {
        this.filterCategoryInputError = this.$t('msg.InvalidInput')
      }
    },

    validateFilterAttribute() {
      return this.filterAttributesAllowed.includes(this.filterAttribute)
    },

    validateFilterCompare() {
      return this.filterComparesAllowed.includes(this.filterCompare)
    },

    validateFilterValue() {
      this.filterValue = this.filterValue.trim()
      return this.filterValue.length <= 30
    },

    validateFilterCategory() {
      this.filterCategory = this.filterCategory.trim()
      if (!this.filterCategory) return true
      return utilStr.checkSlug(this.filterCategory)
    },

    resetFilterError() {
      this.filterInputError = ''
    },

    setRequestedParams(params) {
      this.requestedParams = params
    },

    checkUpdatedReqParams(params) {
      return utilObj.isEqual(this.requestedParams, params) === false
    },
  },
}
</script>

