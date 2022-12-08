<template>
  <div>
    <h1 class="title">{{ $t('page.top') }}</h1>
    <div>
      <h2 class="title">サービスID一覧</h2>
      <service-ids></service-ids>
    </div>
  </div>
</template>
<script>
import ServiceIds from '@/components/organisms/ServiceIds'

export default{
  name: 'Top',

  components: {
    ServiceIds,
  },

  data(){
    return {
    }
  },

  computed: {
  },

  created() {
  }
}
</script>

