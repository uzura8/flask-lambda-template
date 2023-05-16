<template>
<ul>
  <li
    v-for="serviceId in serviceIds"
  >
    <router-link :to="`${urlPrefix}/posts/${serviceId}`">{{serviceId}}</router-link>
  </li>
</ul>
</template>
<script>
import config from '@/config/config'

export default{
  name: 'ServiceIds',

  props: {
    isAdmin: {
      type: Boolean,
      default: false,
    },
  },

  data(){
    return {
    }
  },

  computed: {
    serviceIds() {
      return config.serviceIds
    },

    urlPrefix() {
      return this.isAdmin ? '/admin' : ''
    },
  },

  created() {
  }
}
</script>

