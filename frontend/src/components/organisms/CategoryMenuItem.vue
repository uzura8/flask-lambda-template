<template>
<li>
  <a
    :class="{ 'is-active': activeCategorySlug == category.slug }"
    @click="isExpanded = !isExpanded"
  >
    <span
      class="u-underline"
      @click="linkToCate(category.slug)"
    >
      {{ category.label }}
    </span>
    <b-icon
      class="is-pulled-right"
      pack="fas"
      :icon="isExpanded ? 'caret-up' : 'caret-down'"
    ></b-icon>
  </a>
  <ul :class="{ 'is-active': isExpanded }">
    <li
      v-for="item in category.children"
      :key="item.id"
    >
      <router-link
        :class="{ 'is-active': activeCategorySlug == item.slug }"
        :to="`/posts/${serviceId}/categories/${item.slug}`"
      >{{ item.label }}</router-link>
    </li>
  </ul>
</li>
</template>

<script>
export default {
  name: 'CategoryMenuItem',

  props: {
    category: {
      type: Object,
      default: null,
    },

    activeCategorySlug: {
      type: String,
      default: '',
    },
  },

  data() {
    return {
      isExpanded: false,
    }
  },

  computed: {
  },

  watch: {
    activeCategorySlug(val) {
      this.isExpanded = this.checkHasActiveChildren(val)
    },
  },

  created() {
    if (this.checkHasActiveChildren(this.activeCategorySlug)) {
      this.isExpanded = true
    }
  },

  destroyed() {
  },

  methods: {
    checkHasActiveChildren(currentCateSlug) {
      if (!currentCateSlug) return false
      if (!this.category.children) return false

      for (let h = 0, m = this.category.children.length; h < m; h++) {
        let item = this.category.children[h]
        if (item.slug === currentCateSlug) return true
      }
      return false
    },

    linkToCate(cateSlug) {
      this.$router.push(`/posts/${this.serviceId}/categories/${cateSlug}`)
    },
  }
}
</script>

<style scoped>
ul {
  display: none;

  .is-active {
    display: block;
  }
}
</style>
