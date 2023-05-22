<template>
<div>
  <h1 class="title">{{ $t('common.editOf', {label: $t('common.url')}) }}</h1>
  <admin-shorten-url-form
    v-if="shortenUrl != null"
    :shorten-url="shortenUrl"
  ></admin-shorten-url-form>
</div>
</template>
<script>
import { Admin } from '@/api'
import AdminShortenUrlForm from '@/components/organisms/AdminShortenUrlForm'

export default{
  name: 'AdminShortenUrlEdit',

  components: {
    AdminShortenUrlForm,
  },

  data(){
    return {
      shortenUrl: null,
    }
  },

  computed: {
    urlId() {
      return this.$route.params.urlId
    },
  },

  async created() {
    await this.setShortenUrlObj()
  },

  methods: {
    async setShortenUrlObj() {
      this.$store.dispatch('setLoading', true)
      try {
        this.$store.dispatch('setLoading', false)
        this.shortenUrl = await Admin.getShortenUrls(this.serviceId, this.urlId, null, this.adminUserToken)
      } catch (err) {
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },
  },
}
</script>

