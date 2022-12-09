<template>
<div>
  <h1 class="title">{{ $t('common.createOf', {label: $t('term.shortenUrl')}) }}</h1>
  <admin-shorten-url-form></admin-shorten-url-form>
</div>
</template>
<script>
import AdminShortenUrlForm from '@/components/organisms/AdminShortenUrlForm'

export default{
  name: 'AdminShortenUrl',

  components: {
    AdminShortenUrlForm,
  },

  data(){
    return {
    }
  },

  computed: {
  },

  created() {
  },

  methods: {
  },
}
</script>

