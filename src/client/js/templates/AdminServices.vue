<template>
<div>
  <h1 class="title">{{ $t('page.Services') }}</h1>

  <div>
    <router-link
      :to="`/admin/services/create`"
      class="button"
    >{{ $t('common.createNew') }}</router-link>
  </div>

  <div class="mt-5">
    <service-list></service-list>
  </div>
</div>
</template>
<script>
import ServiceList from '@/components/organisms/ServiceList'

export default{
  name: 'AdminServices',

  components: {
    ServiceList,
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

