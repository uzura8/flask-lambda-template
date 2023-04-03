<template>
<div>
  <h1 class="title">{{ $t('common.editOf', {label: $t('term.service')}) }}</h1>
  <p class="subtitle is-5">ServiceID: {{ serviceId }}</p>
  <admin-service-form
    v-if="service"
    :service="service"
  ></admin-service-form>
</div>
</template>
<script>
import AdminServiceForm from '@/components/organisms/AdminServiceForm'
import { Admin } from '@/api'

export default{
  name: 'AdminService',

  components: {
    AdminServiceForm,
  },

  data(){
    return {
      service: null,
    }
  },

  computed: {
  },

  async created() {
    await this.setService()
  },

  methods: {
    async setService() {
      this.$store.dispatch('setLoading', true)
      try {
        this.service = await Admin.getServices(this.serviceId, null, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },
  },
}
</script>

