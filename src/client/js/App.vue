<template>
<div>
  <eb-admin-navbar v-if="isAdminPath" />
  <eb-navbar v-else />
  <eb-admin-tab-menu-post v-if="isAdminPostPages" />
  <div class="container" v-cloak>
    <div class="columns is-desktop">
      <main class="section column">
        <b-loading :active="isLoading" :is-full-page="true" :canCancel="true"></b-loading>
        <router-view></router-view>
      </main>
      <div
        v-if="!isAdminPath"
        class="column is-3-desktop is-2-widescreen"
      >
        <eb-side-nav-menu></eb-side-nav-menu>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import EbNavbar from '@/components/organisms/EbNavbar'
import EbAdminNavbar from '@/components/organisms/EbAdminNavbar'
import EbAdminTabMenuPost from '@/components/organisms/EbAdminTabMenuPost'
import EbSideNavMenu from '@/components/organisms/EbSideNavMenu'

export default {
  name: 'App',

  components: {
    EbNavbar,
    EbAdminNavbar,
    EbAdminTabMenuPost,
    EbSideNavMenu,
  },

  computed: {
    isLoading() {
      return this.$store.state.common.isLoading
    },

    isAdminPostPages() {
      return this.$route.path.startsWith('/admin/posts')
    },
  },

  methods: {
  },
}
</script>
