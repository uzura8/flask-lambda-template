<template>
<div>
  <h1 class="title">{{ $t('page.adminTop') }}</h1>
  <p>{{ $t('msg.signInGreeting', { name: adminUserName }) }}</p>

  <div v-if="services" class="mt-6">
    <h2 class="title is-4">{{ $t('page.AdminPostManagement') }}</h2>
    <ul>
      <li v-for="service in services">
        <router-link :to="`/admin/posts/${service.serviceId}`">
          <span class="has-text-weight-semibold">{{ service.label }}</span>
          <span class="ml-1">({{ service.serviceId }})</span>
        </router-link>
      </li>
    </ul>
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
        console.log(err);//!!!!!!
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },
  }
}
</script>
