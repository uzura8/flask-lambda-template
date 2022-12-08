<template>
<div>
  <div
    v-if="users.length > 0"
    class="table-container"
  >
    <table class="table">
      <thead>
        <tr>
          <th>Username</th>
          <th>Email</th>
          <th>Role</th>
          <th>ServiceId</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users">
          <td>
            <router-link :to="`/admin/users/${user.username}`">{{ user.username }}</router-link>
          </td>
          <td>{{ user.email }}</td>
          <td v-text="user.role == 'admin' ? $t('term.userRoleAdmin') : $t('term.userRoleNormal')"></td>
          <td v-text="user.acceptServiceIds.join(', ')"></td>
        </tr>
      </tbody>
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
  name: 'AdminUserList',

  props: {
  },

  data(){
    return {
      users: [],
    }
  },

  computed: {
  },

  async created() {
    await this.fetchUsers()
  },

  methods: {
    async fetchUsers(params = {}) {
      const params_copied = { ...params }
      this.$store.dispatch('setLoading', true)
      try {
        const items = await Admin.getUsers(null, params_copied, this.adminUserToken)
        items.map(item => {
          this.users.push(item)
        })
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        console.log(err);//!!!!!!
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    }
  }
}
</script>

