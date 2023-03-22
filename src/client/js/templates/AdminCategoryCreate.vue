<template>
<div>
  <h1 class="title">{{ $t('common.createOf', {label: $t('common.category')}) }}</h1>
  <admin-category-form
    :parent-category-slug-default="parentCategorySlug"
  ></admin-category-form>
</div>
</template>
<script>
import AdminCategoryForm from '@/components/organisms/AdminCategoryForm'

export default{
  name: 'AdminCategoryCreate',

  components: {
    AdminCategoryForm,
  },

  data(){
    return {
    }
  },

  computed: {
    parentCategorySlug() {
      return this.$route.query.parent
    }
  },

  created() {
  },

  methods: {
  },
}
</script>

