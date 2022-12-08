<template>
  <tr>
    <td class="is-size-6">{{ group.slug }}</td>
    <td class="is-size-6">{{ group.label }}</td>
    <td>
      <router-link
        :to="`/admin/posts/${serviceId}/groups/${slug}`"
        class="button is-small"
      >
        <span class="icon is-small">
          <i class="fas fa-pen"></i>
        </span>
      </router-link>
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

