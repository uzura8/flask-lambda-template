<template>
<div>
  <div>
    <h1 class="title">{{ $t('common.postsOf', {label: tagLabel}) }}</h1>
    <p class="subtitle is-5">ServiceID: {{ serviceId }}</p>
  </div>
  <post-list class="mt-6"></post-list>
</div>
</template>
<script>
import PostList from '@/components/organisms/PostList'

export default{
  name: 'PostTags',

  components: {
    PostList,
  },

  computed: {
    tagLabel() {
      return this.$route.params.tagLabel
    },
  },

  created() {
    if (!this.tagLabel) this.$router.push('/error/notfound')
  },
}
</script>

