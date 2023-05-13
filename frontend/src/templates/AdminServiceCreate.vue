<template>
<div>
  <h1 class="title">{{ $t('common.createOf', {label: $t('term.service')}) }}</h1>
  <admin-service-form></admin-service-form>
</div>
</template>
<script>
import AdminServiceForm from '@/components/organisms/AdminServiceForm'

export default{
  name: 'AdminService',

  components: {
    AdminServiceForm,
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

