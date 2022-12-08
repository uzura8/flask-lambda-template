<template>
<div>
  <h1 class="title">{{ $t('common.editOf', {label: $t('term.postGroup')}) }}</h1>
  <admin-post-group-form
    v-if="group != null"
    :group="group"
  ></admin-post-group-form>
</div>
</template>
<script>
import { Admin } from '@/api'
import AdminPostGroupForm from '@/components/organisms/AdminPostGroupForm'

export default{
  name: 'AdminPostGroupEdit',

  components: {
    AdminPostGroupForm,
  },

  data(){
    return {
      group: null,
    }
  },

  computed: {
    slug() {
      return this.$route.params.slug
    },
  },

  async created() {
    await this.setPostGroup()
  },

  methods: {
    async setPostGroup() {
      this.$store.dispatch('setLoading', true)
      try {
        this.$store.dispatch('setLoading', false)
        this.group = await Admin.getPostGroups(this.serviceId, this.slug, null, this.adminUserToken)
      } catch (err) {
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },
  },
}
</script>

