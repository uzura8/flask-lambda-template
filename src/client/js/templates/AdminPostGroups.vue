<template>
<div>
  <div>
    <h1 class="title">{{ $t('page.AdminPostGroupManagement') }}</h1>
    <p class="subtitle is-5">ServiceID: {{ serviceId }}</p>

    <router-link
      :to="`/admin/posts/${serviceId}/groups/create`"
      class="button"
    >{{ $t('common.createNew') }}</router-link>
  </div>
  <div
    v-if="groups.length > 0"
    class="mt-6"
  >
    <table class="table is-fullwidth">
      <thead>
        <tr>
          <th class="is-size-6">{{ $t('form.Slug') }}</th>
          <th class="is-size-6">{{ $t('common.dispLabel') }}</th>
          <th class="is-size-7">{{ $t('common.edit') }}</th>
        </tr>
      </thead>
      <tbody>
        <admin-post-groups-table-row
          v-for="group in groups"
          :key="group.slug"
          :group="group"
          @deleted="deleteGroup"
        ></admin-post-groups-table-row>
      </tbody>
    </table>
  </div>
  <div
    v-else
    class="mt-5"
  >
    <p>{{ $t('msg["Data is empty"]') }}</p>
  </div>
</div>
</template>
<script>
import { Admin } from '@/api'
import AdminPostGroupsTableRow from '@/components/organisms/AdminPostGroupsTableRow'

export default{
  name: 'AdminPostGroups',

  components: {
    AdminPostGroupsTableRow,
  },

  data() {
    return {
      groups: [],
    }
  },

  computed: {
  },

  async created() {
    await this.fetchGroups()
  },

  methods: {
    async fetchGroups() {
      this.$store.dispatch('setLoading', true)
      try {
        let params = {}
        this.groups = await Admin.getPostGroups(this.serviceId, null, params, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        console.log(err)
        this.handleApiError(err, 'Failed to get data from server')
        this.$store.dispatch('setLoading', false)
      }
    },

    deleteGroup(slug) {
      const index = this.groups.findIndex((item) => {
        return item.slug === slug
      })
      if (index === -1) return

      this.groups.splice(index, 1)
    },
  },
}
</script>

