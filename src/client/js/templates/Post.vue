<template>
<div v-if="post">
  <div class="block">
    <router-link :to="isAdminPath ? `/admin/posts/${serviceId}` : `/posts/${serviceId}`">
      <i class="fas fa-chevron-left"></i>
      <span>{{ $t('common.posts') }}</span>
    </router-link>
  </div>

  <h1 class="title">{{ post.title }}</h1>

  <post-body
    v-if="post.bodyHtml"
    :body="post.bodyHtml"
  ></post-body>

  <div
    v-if="votes"
    class="mt-5"
  >
    <vote-unit
      :vote-types="voteTypes"
      :posted-votes="votes"
      :content-id="post.postId"
      @post-vote="postVote"
    ></vote-unit>
  </div>

  <div class="mt-5">
    <time
      itemprop="datepublished"
      :datetime="post.publishAt | dateFormat('')"
    >{{ post.publishAt | dateFormat }}</time>
  </div>

  <nav
    v-if="post.category"
    class="breadcrumb"
    aria-label="breadcrumbs"
  >
    <ul>
      <li>
        <router-link :to="`/posts/${serviceId}/`">{{ $t('common.posts') }}</router-link>
      </li>
      <li
        v-for="parent in post.category.parents"
      >
        <router-link :to="`/posts/${serviceId}/categories/${parent.slug}`">{{ parent.label }}</router-link>
      </li>
      <li>
        <router-link :to="`/posts/${serviceId}/categories/${post.category.slug}`">{{ post.category.label }}</router-link>
      </li>
    </ul>
  </nav>

  <ul v-if="'tags' in post && post.tags">
    <li
      v-for="tag in post.tags"
      class="is-inline-block mr-2"
    >
      <router-link
        :to="`/posts/${serviceId}/tags/${tag.label}`"
        class="tag"
      >{{ tag.label }}</router-link>
    </li>
  </ul>

  <section
    v-if="isEnabledComment"
    class="mt-6"
  >
    <h3 class="title is-4">{{ $t('common.comments') }}</h3>

    <comments
      v-if="post"
      :content-id="post.postId"
    ></comments>
  </section>

</div>
</template>
<script>
import config from '@/config/config'
import { Post, Vote } from '@/api'
import PostBody from '@/components/atoms/PostBody'
import Comments from '@/components/organisms/Comments'
import VoteUnit from '@/components/organisms/VoteUnit'

export default{
  name: 'Post',

  components: {
    PostBody,
    Comments,
    VoteUnit,
  },

  data(){
    return {
      post: null,
      votes: [],
    }
  },

  computed: {
    slug() {
      return this.$route.params.slug
    },

    voteTypes() {
      return config.voteTypesDefault
    },

    isEnabledComment() {
      return config.isEnabledComment
    },

    previewToken() {
      return this.$route.query.token
    },
  },

  watch: {
  },

  async created() {
    await this.setPost()
    await this.fetchVotes()
  },

  methods: {
    async setPost() {
      this.$store.dispatch('setLoading', true)
      try {
        const params = this.previewToken ? { token:this.previewToken } : null
        this.post = await Post.get(this.serviceId, this.slug, params)
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        console.log(err);//!!!!!!
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    async fetchVotes() {
      this.$store.dispatch('setLoading', true)
      try {
        this.votes = await Vote.get(this.serviceId, this.post.postId)
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        console.log(err);//!!!!!!
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    async postVote(voteType) {
      this.$store.dispatch('setLoading', true)
      try {
        const vals = { 'type': voteType }
        this.votes = await Vote.post(this.serviceId, this.post.postId, vals)
        //this.voteCount = res[0].voteCount
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        console.log(err);//!!!!!!
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },
  },
}
</script>

