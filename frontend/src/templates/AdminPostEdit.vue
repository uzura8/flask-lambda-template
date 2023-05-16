<template>
<div>
  <h1 class="title">{{ $t('common.editOf', {label: $t('common.post')}) }}</h1>
  <admin-post-form
    v-if="post != null"
    :post="post"
  ></admin-post-form>
</div>
</template>
<script>
import { Admin } from '@/api'
import AdminPostForm from '@/components/organisms/AdminPostForm'

export default{
  name: 'AdminPost',

  components: {
    AdminPostForm,
  },

  data(){
    return {
      post: null,
    }
  },

  computed: {
    postId() {
      return this.$route.params.postId
    },
  },

  async created() {
    await this.setPost()
  },

  methods: {
    async setPost() {
      this.$store.dispatch('setLoading', true)
      try {
        this.$store.dispatch('setLoading', false)
        this.post = await Admin.getPosts(this.serviceId, this.postId, null, this.adminUserToken)
      } catch (err) {
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },
  },
}
</script>

