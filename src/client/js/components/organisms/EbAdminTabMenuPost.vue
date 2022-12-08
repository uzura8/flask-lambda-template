<template>
<div class="tabs">
  <ul>
    <li :class="{'is-active': this.$route.path === `/admin/posts/${serviceId}`}">
      <router-link
        :to="`/admin/posts/${serviceId}`"
      >{{ $t('common.posts') }}</router-link>
    </li>
    <li :class="{'is-active': this.$route.path === `/admin/posts/${serviceId}/groups`}">
      <router-link
        :to="`/admin/posts/${serviceId}/groups`"
      >{{ $t('page.AdminPostGroupManagement') }}</router-link>
    </li>
  </ul>
</div>
</template>

<script>

export default {
  name: 'EbAdminTabMenuPost',

  data () {
    return {
    }
  },

  computed: {
  },

  created() {
  },

  destroyed() {
  },

  methods: {
  }
}
</script>

