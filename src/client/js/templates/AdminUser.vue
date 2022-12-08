<template>
<div>
  <h1 class="title">{{ $t('page.AdminUserSettings') }}</h1>
  <div class="mt-5">
    <table
      v-if="user"
      class="table"
    >
      <tbody>
        <tr>
          <th>Username</th>
          <td>{{ user.username }}</td>
        </tr>
        <tr>
          <th>Email</th>
          <td>
            <span>{{ user.email }}</span>
            <span
              v-if="user.emailVerified"
              class="has-text-success ml-2"
            >Verified</span>
          </td>
        </tr>
        <tr>
          <th>Role</th>
          <td v-text="user.role == 'admin' ? $t('term.userRoleAdmin') : $t('term.userRoleNormal')"></td>
        </tr>
        <tr>
          <th>Status</th>
          <td>{{ user.status }}</td>
        </tr>
        <tr>
          <th>{{ $t('common.createdAt') }}</th>
          <td>{{ user.createdAt | dateFormat }}</td>
        </tr>
        <tr>
          <th>{{ $t('common.updatedAt') }}</th>
          <td>{{ user.updatedAt | dateFormat }}</td>
        </tr>
      </tbody>
    </table>
  </div>
  <div class="mt-6">
    <h2 class="title is-4">{{ $t('term.acceptServices') }}</h2>
    <section
      v-if="services"
    >
      <b-field
        v-for="service in services"
        :key="service.serviceId"
      >
        <b-checkbox
          v-model="selectedServiceIds"
          :native-value="service.serviceId"
        >
          <span class="has-text-weight-semibold">{{ service.serviceId }}</span>
          <span>{{ service.label }}</span>
        </b-checkbox>
      </b-field>
      <p
        v-if="selectedServiceIdsError"
        class="has-text-danger"
      >{{ selectedServiceIdsError }}</p>
    </section>
  </div>
</div>
</template>
<script>
import { Admin } from '@/api'
import arr from '@/util'

export default{
  name: 'AdminUser',

  components: {
  },

  data(){
    return {
      services: null,
      user: null,
      selectedServiceIds: null,
      selectedServiceIdsError: '',
    }
  },

  computed: {
    username () {
      return this.$route.params.username
    },

    serviceIds () {
      let serviceIds = []
      this.services.map(item => serviceIds.push(item))
      return serviceIds
    },
  },

  watch: {
    async selectedServiceIds(val, oldVal) {
			if (oldVal === null) return

      this.selectedServiceIdsError = ''
      await this.updateServiceIds()
    },
  },

  async created() {
    await this.setServices()
    await this.fetchUser()
    this.setSelectedServiceIds()
  },

  methods: {
    async fetchUser(params = {}) {
      const params_copied = { ...params }
      this.$store.dispatch('setLoading', true)
      try {
        this.user = await Admin.getUsers(this.username, params_copied, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        console.log(err);//!!!!!!
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    async setServices(params = {}) {
      const params_copied = { ...params }
      this.$store.dispatch('setLoading', true)
      try {
        this.services = await Admin.getServices(null, params_copied, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        console.log(err);//!!!!!!
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    async updateServiceIds() {
      if (this.validateServiceIds() === false) {
      }

      try {
        let vals = {}
        vals.serviceIds = this.selectedServiceIds
        this.$store.dispatch('setLoading', true)
        const res = await Admin.updateUser(this.username, vals, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
        this.showGlobalMessage(this.$t('msg.Updated'), 'is-success')
      } catch (err) {
        console.log(err);//!!!!!!
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Update failed"]'))
      }
    },

    setSelectedServiceIds() {
      if (! this.user) return
      if ('acceptServiceIds' in this.user === false) return
      if (! this.user.acceptServiceIds) return

      this.selectedServiceIds = this.user.acceptServiceIds
    },

    validateServiceIds() {
      if (this.selectedServiceIds.length === 0) return true
      const res = this.selectedServiceIds.filter(item => this.serviceIds.includes(item) === false)
      return res.length === 0
    },
  },
}
</script>

