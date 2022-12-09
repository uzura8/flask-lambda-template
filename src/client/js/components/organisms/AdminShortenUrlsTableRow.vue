<template>
  <tr>
    <td>
      <router-link :to="`/admin/shorten-urls/${serviceId}/${shortenUrl.urlId}`">{{ shortenUrl.urlId }}</router-link>
    </td>
    <td>{{ shortenUrl.name }}</td>
    <td class="is-size-7">{{ shortenUrl.url }}</td>
    <td class="is-size-6 has-text-success">
      <i
        v-if="shortenUrl.isViaJumpPage"
        class="fas fa-check"
      ></i>
    </td>
    <td>
      <router-link
        :to="`/admin/shorten-urls/${serviceId}/${shortenUrl.urlId}/edit`"
        class="button is-small"
      >
        <span class="icon is-small">
          <i class="fas fa-pen"></i>
        </span>
      </router-link>
    </td>
    <td class="is-size-7"><inline-time :datetime="shortenUrl.createdAt"></inline-time></td>
  </tr>
</template>
<script>
import InlineTime from '@/components/atoms/InlineTime'

export default{
  name: 'AdminShortenUrlsTableRow',

  components: {
    InlineTime,
  },

  props: {
    shortenUrl: {
      type: Object,
      default: null,
    },
  },

  data(){
    return {
    }
  },

  computed: {
  },

  watch: {
  },

  created() {
  },

  methods: {
  },
}
</script>

