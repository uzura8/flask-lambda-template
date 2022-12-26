<template>
<div>
  <div>
    <h1 class="title">{{ $t('common.posts') }}</h1>
    <p class="subtitle is-5">ServiceID: {{ serviceId }}</p>

    <div
      v-if="outerSiteUrl"
      class="is-pulled-right"
    >
      <a :href="outerSiteUrl" target="_blank">
        <i class="fas fa-globe-asia"></i>
        <span>{{ $t('common.webSite') }}</span>
      </a>
    </div>

    <router-link
      v-if="hasEditorRole"
      :to="`/admin/posts/${this.serviceId}/create`"
      class="button"
    >{{ $t('common.createNew') }}</router-link>
  </div>
  <admin-post-list class="mt-6"></admin-post-list>
</div>
</template>
<script>
import { Admin } from '@/api'
import common from '@/util/common'
import AdminPostList from '@/components/organisms/AdminPostList'

export default{
  name: 'AdminPosts',

  components: {
    AdminPostList,
  },

  data() {
    return {
      service: null,
    }
  },

  computed: {
    outerSiteUrl() {
      if (this.service == null) return ''
      if (common.checkObjHasProp(this.service, 'configs') === false) return ''
      if (common.checkObjHasProp(this.service.configs, 'outerSiteUrl') === false) return ''
      return this.service.configs.outerSiteUrl
    },
  },

  async created() {
    await this.setService()
  },

  methods: {
    async setService() {
      this.service = await Admin.getServices(this.serviceId, null, this.adminUserToken)
    },
  },
}
</script>

