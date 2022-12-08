<template>
<div>
  <aside
    v-if="serviceId && (categories || tags)"
    class="menu"
  >
    <p class="menu-label">{{ $t('common.categories') }}</p>
    <ul class="menu-list">
      <category-menu-item
        v-for="category in categories"
        :key="category.id"
        :category="category"
        :active-category-slug="currenCategorySlug"
      ></category-menu-item>
    </ul>

    <p class="menu-label">{{ $t('common.tags') }}</p>
    <ul class="menu-list">
      <tag-menu-item
        v-for="tag in tags"
        :key="tag.tagId"
        :tag="tag"
        :active-label="currenTagLabel"
      ></tag-menu-item>
    </ul>

    <p class="menu-label">{{ $t('term.postGroup') }}</p>
    <ul class="menu-list">
      <li
        v-for="group in groups"
        :key="group.slug"
      >
        <router-link
          :class="{ 'is-active': currenPostGroupSlug === group.slug }"
          :to="`/posts/${serviceId}/groups/${group.slug}`"
        >{{ group.label }}</router-link>
      </li>
    </ul>
  </aside>
</div>
</template>
<script>
import { Category, Tag, Post } from '@/api'
import CategoryMenuItem from '@/components/organisms/CategoryMenuItem'
import TagMenuItem from '@/components/molecules/TagMenuItem'

export default {
  name: 'EbSideNavMenu',

  components: {
    CategoryMenuItem,
    TagMenuItem,
  },

  props: {
  },

  data() {
    return {
      categories: [],
      tags: [],
      groups: [],
    }
  },

  computed: {
    currenCategorySlug() {
      return this.$route.params.categorySlug
    },

    currenTagLabel() {
      return this.$route.params.tagLabel
    },

    currenPostGroupSlug() {
      if (this.$route.path.startsWith(`/posts/${this.serviceId}/groups/`) === false) return ''
      return this.$route.params.slug
    },
  },

  watch: {
    async serviceId(val, oldVal) {
      await this.fetchCategories()
      await this.fetchTags()
      await this.fetchPostGroups()
    },
  },

  created() {
  },

  methods: {
    async fetchCategories() {
      if (!this.serviceId) return
      this.$store.dispatch('setLoading', true)
      try {
        const params = { withChildren: 1 }
        const res = await Category.get(this.serviceId, 'root', params)
        this.categories = ('children' in res && res.children) ? res.children : []
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        this.$store.dispatch('setLoading', false)
        if (err.response.status === 404) {
          return
        }
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    async fetchTags() {
      if (!this.serviceId) return
      this.$store.dispatch('setLoading', true)
      try {
        const res = await Tag.getAll(this.serviceId)
        this.tags = res
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        this.$store.dispatch('setLoading', false)
        if (err.response.status === 404) {
          return
        }
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    async fetchPostGroups() {
      if (!this.serviceId) return
      this.$store.dispatch('setLoading', true)
      try {
        const res = await Post.getGroups(this.serviceId)
        this.groups = res
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        this.$store.dispatch('setLoading', false)
        if (err.response.status === 404) {
          return
        }
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },
  }
}
</script>
