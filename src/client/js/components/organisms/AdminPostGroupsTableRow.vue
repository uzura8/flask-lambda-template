<template>
  <tr>
    <td class="is-size-6 w-180">{{ group.slug }}</td>
    <td class="is-size-6">
      <router-link
        :to="`/admin/posts/${serviceId}/groups/${group.slug}`"
      >{{ group.label }}</router-link>
    </td>
  </tr>
</template>
<script>
import { Admin } from '@/api'

export default{
  name: 'AdminPostGroupsTableRow',

  components: {
  },

  props: {
    group: {
      type: Object,
      default: null,
    },
  },

  data(){
    return {
    }
  },

  computed: {
    slug() {
      return this.group.slug
    }
  },

  watch: {
  },

  created() {
  },

  methods: {
  },
}
</script>
<style lang="scss" scoped>
.w-180 {
  width: 180px;
}
</style>
