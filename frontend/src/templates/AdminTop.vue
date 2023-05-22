<template>
<div>
  <h1 class="title">{{ $t('page.adminTop') }}</h1>
  <p>{{ $t('msg.signInGreeting', { name: adminUserName }) }}</p>

  <div v-if="services" class="mt-6">
    <div
      v-for="service in services"
      :key="service.serviceId"
      class="box"
    >
      <h3 class="title is-4">
        <span>{{ service.label }}</span>
        <span class="ml-1 has-text-weight-normal is-size-6">({{ service.serviceId }})</span>
      </h3>
      <div v-if="service.functions" class="block">
        <ul>
          <li
            v-for="functionKey in service.functions"
            class="is-size-5 mt-2"
          >
            <router-link :to="getFunctionUrl(service.serviceId, functionKey)">
              {{ $t(`page.adminFunctions["${functionKey}"]`) }}
            </router-link>
          </li>
        </ul>
      </div>
      <div v-else>{{ $t('msg["No Data"]') }}</div>
    </div>
  </div>
</div>
</template>
<script>
import { Admin } from '@/api'

export default{
  name: 'AdminTop',

  components: {
  },

  data(){
    return {
      services: [],
    }
  },

  computed: {
  },


  async created() {
    await this.fetchServices()
    //if (this.services.length === 1) {
    //  this.$router.push(`/admin/posts/${this.services[0].serviceId}`)
    //}
  },

  methods: {
    async fetchServices(params = {}) {
      const params_copied = { ...params }
      this.$store.dispatch('setLoading', true)
      try {
        const res = await Admin.getAccountServices(params_copied, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
        this.services = res
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    getFunctionUrl(serviceId, functinKey) {
      let path = ''
      switch (functinKey) {
        case 'post':
          path = 'posts'
          break
        case 'urlShortener':
          path = 'shorten-urls'
          break
      }
      if (!path) return ''
      return `/admin/${path}/${serviceId}`
    },
  }
}
</script>
