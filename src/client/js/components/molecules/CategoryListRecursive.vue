<template>
<ul class="ml-5">
  <li
    v-for="cate in categories"
    :key="cate.slug"
    :value="cate.slug"
    class="list-box"
  >
    <a
      @click="toggleBlock(cate.slug)"
      class="u-clickable list-label has-text-black"
    >
      <span>{{ cate.label }}</span>
      <span class="icon is-pulled-right">
        <i  v-if="activeCateSlugs.includes(cate.slug)" class="fas fa-angle-up"></i>
        <i v-else class="fas fa-angle-down"></i>
      </span>
    </a>
    <ul
      v-if="hasEditorRole && activeCateSlugs.includes(cate.slug)"
      class="is-flex ml-5 mb-3"
    >
      <li class="mr-5">
        <router-link
          v-if="activeCateSlugs.includes(cate.slug)"
          :to="{path:`/admin/categories/${serviceId}/create`, 'query':{parent:cate.slug}}"
          class="u-clickable icon-text is-size-6i has-text-grey"
        >
          <span class="icon">
            <i class="fas fa-plus"></i>
          </span>
          <span>{{ $t('common.add') }}</span>
        </router-link>
      </li>
      <li>
        <router-link
          v-if="activeCateSlugs.includes(cate.slug)"
          :to="`/admin/categories/${serviceId}/${cate.slug}/edit`"
          class="u-clickable icon-text is-size-6 has-text-grey"
        >
          <span class="icon">
            <i class="fas fa-edit"></i>
          </span>
          <span>{{ $t('common.edit') }}</span>
        </router-link>
      </li>
    </ul>

    <category-list-recursive
      v-if="activeCateSlugs.includes(cate.slug)"
      :parent-category-slug="cate.slug"
    ></category-list-recursive>

  </li>
</ul>
</template>
<script>
import { Category } from '@/api'
import CategoryListRecursive from '@/components/molecules/CategoryListRecursive'

export default{
  name: 'CategoryListRecursive',

  components: {
    CategoryListRecursive,
  },

  props: {
    parentCategorySlug: {
      type: String,
      required: true,
    },
  },

  data(){
    return {
      //cateSlug: '',
      categories: [],
      activeCateSlugs: [],
      isHide: false,
    }
  },

  computed: {
  },

  watch: {
  },

  async created() {
    await this.setCategories(this.parentCategorySlug)
  },

  methods: {
    async setCategories(parentCateSlug) {
      this.$store.dispatch('setLoading', true)
      try {
        this.categories.splice(0, this.categories.length);
        const items = await Category.getChildren(this.serviceId, parentCateSlug)
        items.map((item) => {
          this.categories.push(item)
        })
        if (this.checkEmpty(items)) this.isHide = true
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        console.log(err);//!!!!!!
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    toggleBlock(cateSlug) {
      const index = this.activeCateSlugs.findIndex(item => item === cateSlug)
      if (index === -1) {
        this.activeCateSlugs.push(cateSlug)
      } else {
        this.activeCateSlugs.splice(index, 1)
      }
    },
  },
}
</script>
<style>
.list-box {
  border-bottom: 1px solid #dbdbdb;

  &:last-child {
    border-bottom: none;
  }

  .list-label {
    display: block;
    padding: 15px 0;
    font-size: 1.25rem;
  }
}
</style>

