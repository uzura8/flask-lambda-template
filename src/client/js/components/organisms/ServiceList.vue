<template>
<div>
  <div
    v-if="services.length > 0"
    class="table-container"
  >
    <table class="table">
      <tr>
        <th>serviceId</th>
        <th>label</th>
        <th>Edit</th>
      </tr>
      <tr
        v-for="service in services"
      >
        <td class="has-text-weight-semibold">{{ service.serviceId }}</td>
        <td>{{ service.label }}</td>
        <td>
          <router-link
            :to="`/admin/services/${service.serviceId}/edit`"
          >
            <span class="icon"><i class="fas fa-edit"></i></span>
          </router-link>
        </td>
      </tr>
    </table>
  </div>
  <div v-else-if="!isLoading">
    <p>{{ $t('msg["Data is empty"]') }}</p>
  </div>
</div>
</template>
<script>
import { Admin } from '@/api'

export default{
  name: 'AdminServiceList',

  props: {
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
  },

  methods: {
    async fetchServices(params = {}) {
      const params_copied = { ...params }
      this.$store.dispatch('setLoading', true)
      try {
        const items = await Admin.getServices(null, params_copied, this.adminUserToken)
        items.map(item => {
          this.services.push(item)
        })
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    }
  }
}
</script>

