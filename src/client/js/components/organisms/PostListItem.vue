<template>
<div class="card">
  <div class="card-content">
    <div class="media">
      <div class="media-content">
        <h4 class="title is-4">
          <router-link
            :to="`/posts/${serviceId}/${post.slug}`"
          >{{ post.title }}</router-link>
        </h4>
      </div>
    </div>

    <div class="content">
      <div v-text="post.bodyText"></div>
      <div class="mt-5">
        <time
          itemprop="datepublished"
          :datetime="post.publishAt | dateFormat('')"
        >{{ post.publishAt | dateFormat }}</time>
      </div>
    </div>
  </div>
</div>
</template>
<script>
export default{
  name: 'PostListItem',

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
  },

  watch: {
  },

  created() {
  },

  methods: {
  },
}
</script>

