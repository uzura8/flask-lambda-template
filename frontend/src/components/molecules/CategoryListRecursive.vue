<template>
<div class="">
  <draggable
    v-model="categories"
    :group="`categoryGroup-${parentCategorySlug}`"
    :options="{handle:'.handle'}"
    @start="drag=true"
    @end="drag=false"
    @update="updateCategoriesOrder"
  >
    <div
      v-for="cate in categories"
      :key="cate.slug"
      class="list-box"
      v-if="deletedCateSlugs.includes(cate.slug) === false"
    >
      <button
        v-if="hasEditorRole"
        class="button is-small handle"
      >
        <span class="icon is-small">
          <i class="fas fa-sort"></i>
        </span>
      </button>
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
        v-if="activeCateSlugs.includes(cate.slug)"
        class="is-flex mb-3"
      >
        <li
          v-if="hasEditorRole"
          class="mr-5"
        >
          <router-link
            :to="{path:`/admin/categories/${serviceId}/create`, 'query':{parent:cate.slug}}"
            class="icon-text is-size-6i has-text-grey"
          >
            <span class="icon">
              <i class="fas fa-plus"></i>
            </span>
            <span>{{ $t('common.add') }}</span>
          </router-link>
        </li>
        <li
          v-if="hasEditorRole"
          class="mr-5"
        >
          <router-link
            :to="`/admin/categories/${serviceId}/${cate.slug}/edit`"
            class="icon-text is-size-6 has-text-grey"
          >
            <span class="icon">
              <i class="fas fa-edit"></i>
            </span>
            <span>{{ $t('common.edit') }}</span>
          </router-link>
        </li>
        <li
          v-if="hasEditorRole"
          class="mr-5"
        >
          <a
            @click="confirmDeleteCategory(cate.slug)"
            class="u-clickable icon-text is-size-6 has-text-grey"
          >
            <span class="icon">
              <i class="fas fa-trash"></i>
            </span>
            <span>{{ $t('common.delete') }}</span>
          </a>
        </li>
        <li class="mr-5">
          <router-link
            :to="{path:`/admin/posts/${serviceId}`, 'query':{category:cate.slug}}"
            class="u-clickable icon-text is-size-6 has-text-grey"
          >{{ $t('common.posts') }}</router-link>
        </li>
      </ul>

      <category-list-recursive
        v-if="activeCateSlugs.includes(cate.slug)"
        :parent-category-slug="cate.slug"
      ></category-list-recursive>

    </div>
  </draggable>
</div>
</template>
<script>
import draggable from 'vuedraggable'
import { Category, Admin } from '@/api'
import CategoryListRecursive from '@/components/molecules/CategoryListRecursive'

export default{
  name: 'CategoryListRecursive',

  components: {
    draggable,
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
      categories: [],
      activeCateSlugs: [],
      deletedCateSlugs: [],
    }
  },

  computed: {
    categoryIds() {
      if (this.checkEmpty(this.categories) === true) return []
      return this.categories.map(item => item.id)
    },
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
        const items = await Admin.getCategoryChildrenByParentSlug(this.serviceId, parentCateSlug, null, this.adminUserToken)
        items.map((item) => {
          this.categories.push(item)
        })
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    confirmDeleteCategory(cateSlug) {
      this.$buefy.dialog.confirm({
        title: this.$t('msg.DeleteFor', {'target': this.$t('common.category')}),
        message: this.$t('msg.cofirmToDelete'),
        confirmText: this.$t('common.delete'),
        type: 'is-danger',
        hasIcon: true,
        onConfirm: async () => {
          await this.deleteCategory(cateSlug)
        },
      })
    },

    async deleteCategory(cateSlug) {
      this.$store.dispatch('setLoading', true)
      try {
        await Admin.deleteCategory(this.serviceId, cateSlug, this.adminUserToken)
        this.deletedCateSlugs.push(cateSlug)
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Delete failed"]'))
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

    async updateCategoriesOrder() {
      try {
        this.$store.dispatch('setLoading', true)
        const vals = { sortedIds: this.categoryIds }
        await Admin.updateCategoriesOrder(this.serviceId, this.parentCategorySlug, vals, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t(`msg["Delete failed"]`))
      }
    },
  },
}
</script>
<style>
.list-box {
  border-bottom: 1px solid #dbdbdb;
  position: relative;
  padding-left: 40px;

  &:last-child {
    border-bottom: none;
  }

  .list-label {
    display: block;
    padding: 15px 0;
    font-size: 1.25rem;
  }

  .handle {
    position: absolute;
    top: 15px;
    left: 0;
  }
}
</style>

