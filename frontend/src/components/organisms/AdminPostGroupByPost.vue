<template>
<div>
  <span
    class="icon u-clickable p-3"
    @click="updatePostGroupPostIdsRegistered"
  >
    <i
      v-if="isRegistered"
      class="fas fa-star has-text-warning"
    ></i>
    <i
      v-else
      class="far fa-star has-text-grey"
    ></i>
  </span>
  <span class="p-3">{{ group.label }}</span>
</div>
</template>
<script>
import obj from '@/util/obj'
import { Admin } from '@/api'

export default{
  components: {
  },

  props: {
    group: {
      type: Object,
      required: true,
    },

    postId: {
      type: String,
      required: true,
    },

    initialPostIds: {
      type: Array,
      required: true,
    },
  },

  data(){
    return {
      postIds: [],
    }
  },

  computed: {
    isRegistered() {
      return this.postIds.includes(this.postId)
    },
  },

  watch: {
  },

  created() {
    this.postIds = this.initialPostIds
  },

  methods: {
    async updatePostGroupPostIdsRegistered() {
      let params = {}
      this.$store.dispatch('setLoading', true)
      try {
        const updStatus = this.isRegistered ? false : true
        const vals = {
          postId: this.postId,
          isRegister: updStatus ? 1 : 0
        }
        this.groups = await Admin.updatePostGroupPostIdsRegistered(
          this.serviceId,
          this.group.slug,
          vals,
          this.adminUserToken
        )
        this.updatedRegisterStatus(updStatus)
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    updatedRegisterStatus(isRegister) {
      if (this.isRegistered) {
        if (isRegister === true) return
        const idx = this.postIds.indexOf(this.postId)
        if (idx === -1) return
        this.postIds.splice(idx, 1);
      } else {
        if (isRegister === false) return
        this.postIds.push(this.postId)
      }
    }
  },
}
</script>

