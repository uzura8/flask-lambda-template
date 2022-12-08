<template>
<div>
  <h1 class="title">{{ $t('common.createOf', {label: $t('term.postGroup')}) }}</h1>
  <admin-post-group-form></admin-post-group-form>
</div>
</template>
<script>
import AdminPostGroupForm from '@/components/organisms/AdminPostGroupForm'

export default{
  name: 'AdminPostGroupCreate',

  components: {
    AdminPostGroupForm,
  },
}
</script>

