<template>
<div>
  <h1 class="title">{{ $t('page.AdminUsers') }}</h1>

  <div class="mt-5">
    <admin-user-list></admin-user-list>
  </div>
</div>
</template>
<script>
import AdminUserList from '@/components/organisms/AdminUserList'

export default{
  name: 'AdminServices',

  components: {
    AdminUserList,
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

