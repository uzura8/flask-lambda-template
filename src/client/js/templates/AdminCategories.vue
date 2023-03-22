<template>
  <div>
    <h1 class="title">{{ $t('page.AdminPostCategoryManagement') }}</h1>

    <div
      v-if="hasEditorRole"
      class="block"
    >
      <a
        v-if="isUseModalForCreate"
        class="button"
        @click="isModalActive = true"
      >{{ $t('common.createNew') }}</a>
      <router-link
        v-else
        :to="{path:`/admin/categories/${serviceId}/create`, 'query':{parent:'root'}}"
        class="button"
      >{{ $t('common.createNew') }}</router-link>
    </div>

    <div>
      <category-list-recursive
        parent-category-slug="root"
      ></category-list-recursive>
    </div>
  </div>
</template>
<script>
import CategoryListRecursive from '@/components/molecules/CategoryListRecursive'

export default{
  name: 'AdminPostCategories',

  components: {
    CategoryListRecursive,
  },

  data(){
    return {
      isUseModalForCreate: false,
      isModalActive: false,
    }
  },

  created() {
  }
}
</script>
