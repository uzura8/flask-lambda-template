<template>
  <tr :class="rowBgColoerClass">
    <td>
      <span v-if="publishStatus == 'published'" class="tag is-success">{{ $t('common.published') }}</span>
      <span v-else-if="publishStatus == 'reserved'" class="tag is-warning">{{ $t('common.reserved') }}</span>
      <span v-else class="tag is-danger">{{ $t('common.unpublished') }}</span>
    </td>
    <td>
      <router-link :to="`/admin/posts/${serviceId}/${post.postId}`">{{ post.title }}</router-link>
    </td>
    <td v-text="'category' in post && post.category ? post.category.label : '-'"></td>
    <td>
      <router-link
        :to="`/admin/posts/${serviceId}/${post.postId}/edit`"
        class="button is-small"
      >
        <span class="icon is-small">
          <i class="fas fa-pen"></i>
        </span>
      </router-link>
    </td>
    <td class="is-size-7"><inline-time :datetime="post.publishAt"></inline-time></td>
    <td class="is-size-7"><inline-time :datetime="post.updatedAt"></inline-time></td>
  </tr>
</template>
<script>
import InlineTime from '@/components/atoms/InlineTime'

export default{
  name: 'AdminPostsTableRow',

  components: {
    InlineTime,
  },

  props: {
    post: {
      type: Object,
      default: null,
    },
  },

  data(){
    return {
    }
  },

  computed: {
    publishStatus() {
      return this.getPostPublishStatus(this.post.postStatus, this.post.publishAt)
    },

    categoryLabel() {
      if ('category' in this.post === false) return '-'
      if (this.checkEmpty(this.post.category)) return '-'
      if (this.checkEmpty(this.post.category.label)) return '-'
      return this.post.category.label
    },

    rowBgColoerClass() {
      const publishStatus = this.getPostPublishStatus(this.post.postStatus, this.post.publishAt)
      switch (publishStatus) {
        case 'unpublished':
          return 'has-background-danger-light'
        case 'reserved':
          return 'has-background-warning-light'
        default :
          return ''
      }
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

