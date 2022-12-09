<template>
<div>
  <div>
    <h1 class="title">{{ $t('page.ShortenUrlList') }}</h1>

    <router-link
      :to="`/admin/shorten-urls/${serviceId}/create`"
      class="button"
    >{{ $t('common.createNew') }}</router-link>
  </div>
  <admin-shorten-url-list class="mt-6"></admin-shorten-url-list>
</div>
</template>
<script>
import AdminShortenUrlList from '@/components/organisms/AdminShortenUrlList'

export default{
  name: 'AdminShortenUrls',

  components: {
    AdminShortenUrlList,
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

