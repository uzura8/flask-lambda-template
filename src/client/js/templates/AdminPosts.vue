<template>
<div>
  <div>
    <h1 class="title">{{ $t('common.posts') }}</h1>
    <p class="subtitle is-5">ServiceID: {{ serviceId }}</p>

    <router-link
      :to="`/admin/posts/${serviceId}/create`"
      class="button"
    >{{ $t('common.createNew') }}</router-link>
  </div>
  <admin-post-list class="mt-6"></admin-post-list>
</div>
</template>
<script>
import AdminPostList from '@/components/organisms/AdminPostList'

export default{
  name: 'AdminPosts',

  components: {
    AdminPostList,
  },

  data() {
    return {
    }
  },

  computed: {
  },

  created() {
  },

  methods: {
  },
}
</script>

