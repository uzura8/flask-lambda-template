<template>
<div v-if="post">

  <b-message
    v-if="isPublished === false"
    type="is-warning"
  >{{ $t('msg.thisIsNotPublished', {name: $t('common.post')}) }}</b-message>

  <b-message
    v-if="post.isHiddenInList === true"
  >{{ $t('msg.hiddenInList') }}</b-message>

  <div class="block">
    <router-link :to="postsPageUri">
      <i class="fas fa-chevron-left"></i>
      <span>{{ $t('common.posts') }}</span>
    </router-link>
  </div>

  <h1 class="title">
    <span
      v-if="isPublishItem === false"
      class="tag is-dark"
    >{{ $t('common.unpublished') }}</span>

    {{ post.title }}
  </h1>

  <div class="is-pulled-right">
    <eb-dropdown
      position="is-bottom-left"
    >
      <span
        slot="label"
        class="icon"
      >
        <i class="fas fa-edit"></i>
      </span>
      <div class="dropdown-content">
        <a
          v-if="previewUrl"
          :href="previewUrl"
          target="_blank"
          class="dropdown-item"
        >
          <span class="icon">
            <i class="fas fa-eye"></i>
          </span>
          <span>{{ $t('common.preview') }}</span>
        </a>

        <router-link
          :to="`/admin/posts/${serviceId}/${post.postId}/edit`"
          class="dropdown-item"
        >
          <span class="icon">
            <i class="fas fa-pen"></i>
          </span>
          <span>{{ $t('common.edit') }}</span>
        </router-link>

        <a
          v-if="isPublishItem"
          @click="updateStatus(false)"
          class="dropdown-item is-clickable"
        >
          <span class="icon">
            <i class="fas fa-lock"></i>
          </span>
          <span>{{ $t('common.unpublish') }}</span>
        </a>

        <a
          v-else
          @click="confirmPublish()"
          class="dropdown-item is-clickable"
        >
          <span class="icon">
            <i class="fas fa-globe"></i>
          </span>
          <span>{{ $t('common.publish') }}</span>
        </a>

        <a
          @click="confirmDelete()"
          class="dropdown-item is-clickable"
        >
          <span class="icon">
            <i class="fas fa-trash"></i>
          </span>
          <span>{{ $t('common.delete') }}</span>
        </a>

      </div>
    </eb-dropdown>
  </div>

  <post-body
    :body="post.bodyHtml"
  ></post-body>

  <ul class="mt-5">
    <li v-if="'images' in post && post.images.length > 0">
      <span>
        <button
          class="button is-ghost"
          @click="isImagesModalActive = true"
        >
          <span class="icon">
            <i class="fas fa-images"></i>
          </span>
          <span>{{ post.images.length }}</span>
        </button>
      </span>
      <b-modal
        v-model="isImagesModalActive"
        :destroy-on-hide="false"
        aria-role="dialog"
        close-button-aria-label="Close"
        aria-modal
      >
        <template #default="props">
          <ul>
            <li v-for="image in post.images" class="mb-5">
              <div class="card">
                <div class="card-image">
                  <fb-img
                    :fileId="image.fileId"
                    :mimeType="image.mimeType"
                    size="raw"
                  />
                </div>
                <div
                  v-if="image.caption"
                  class="card-content"
                >
                  <div class="media">
                    <div class="media-content">{{ image.caption }}</div>
                  </div>
                </div>
              </div>
            </li>
          </ul>
        </template>
      </b-modal>
    </li>

    <li v-if="'files' in post && post.files.length > 0">
      <label>{{ $t('common.files') }}</label>
      <ul>
        <li v-for="file in post.files">
          <a
            :href="mediaUrl('file', file.fileId, file.mimeType)"
            target="_blank"
            v-text="file.caption ? file.caption : file.fileId"
          ></a>
        </li>
      </ul>
    </li>

    <li v-if="'links' in post && post.links.length > 0">
      <label>{{ $t('common.links') }}</label>
      <ul>
        <li v-for="link in post.links">
          <a
            :href="link.url"
            target="_blank"
            v-text="link.label ? link.label : link.url"
          ></a>
        </li>
      </ul>
    </li>

    <li v-if="'category' in post && post.category">
      <label>{{ $t('common.category') }}</label>
      <span>{{ post.category.label }}</span>
    </li>
    <li v-if="'tags' in post && post.tags">
      <label>{{ $t('common.tag') }}</label>
      <span>
        <span
          v-for="tag in post.tags"
          class="tag ml-2"
          >{{ tag.label }}</span>
      </span>
    </li>
    <li>
      <label>{{ $t('common.publishAt') }}</label>
      <inline-time
        :time-class="isReserved ? 'has-text-warning-dark' : ''"
        :datetime="post.publishAt"
      ></inline-time>
      <span v-if="isReserved" class="tag is-warning">{{ $t('common.reserved') }}</span>
    </li>
    <li>
      <label>{{ $t('common.lastUpdatedAt') }}</label>
      <inline-time :datetime="post.updatedAt"></inline-time>
    </li>
  </ul>

</div>
</template>
<script>
import moment from '@/moment'
import { Admin } from '@/api'
import PostBody from '@/components/atoms/PostBody'
import InlineTime from '@/components/atoms/InlineTime'
import EbDropdown from '@/components/molecules/EbDropdown'
import FbImg from '@/components/atoms/FbImg'

export default{
  name: 'AdminPost',

  components: {
    InlineTime,
    EbDropdown,
    PostBody,
    FbImg,
  },

  data(){
    return {
      post: null,
      isImagesModalActive: false,
    }
  },

  computed: {
    postId() {
      return this.$route.params.postId
    },

    isPublished() {
      if (!this.post) return false
      return this.checkPostPublished(this.post.postStatus, this.post.publishAt)
    },

    isPublishItem() {
      if (!this.post) return false
      return this.post.postStatus === 'publish'
    },

    isReserved() {
      return this.getPostPublishStatus(this.post.postStatus, this.post.publishAt) === 'reserved'
    },

    postsPageUri() {
      const uri = `/admin/posts/${this.serviceId}`
      if (!this.$store.state.adminPostsPager.lastIndex) return uri
      return `${uri}?index=${this.$store.state.adminPostsPager.lastIndex}`
    },

    previewUrl() {
      if (!this.post) return ''
      if ('service' in this.post === false) return ''
      if ('frontendPostDetailUrlPrefix' in this.post.service === false) return ''

      const previewUrlPrefix = this.post.service.frontendPostDetailUrlPrefix
      const previewUrl = `${previewUrlPrefix}${this.post.slug}`
      if (this.isPublished) return previewUrl

      if (this.checkEmpty(this.post.previewToken)) return ''
      return `${previewUrl}?token=${this.post.previewToken}`
    },
  },

  async created() {
    await this.getPost()
  },

  methods: {
    async getPost() {
      this.post = await Admin.getPosts(this.serviceId, this.postId, null, this.adminUserToken)
    },

    confirmPublish() {
      this.$buefy.dialog.confirm({
        message: this.$t('msg.cofirmToPublish'),
        onConfirm: async () => await this.updateStatus(true)
      })
    },

    async updateStatus(isPublish = false) {
      try {
        this.$store.dispatch('setLoading', true)
        const postStatus = isPublish ? 'publish' : 'unpublish'
        const res = await Admin.updatePostStatus(this.serviceId, this.postId, postStatus, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
        this.post = res
        this.$emit('posted', res)
        this.showGlobalMessage(this.$t('msg.changePublishStatusCompleted'), 'is-success')
      } catch (err) {
        console.log(err);//!!!!!!
        this.$store.dispatch('setLoading', false)
        if (this.checkResponseHasErrorMessage(err, true)) {
          this.setErrors(err.response.data.errors)
        }
        this.handleApiError(err, this.$t(`msg["Edit failed"]`))
      }
    },

    confirmDelete() {
      this.$buefy.dialog.confirm({
        message: this.$t('msg.cofirmToDelete'),
        onConfirm: async () => await this.deletePost()
      })
    },

    async deletePost() {
      try {
        this.$store.dispatch('setLoading', true)
        const res = await Admin.deletePost(this.serviceId, this.postId, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
        this.$router.push(`/admin/posts/${this.serviceId}`)
      } catch (err) {
        console.log(err);//!!!!!!
        this.$store.dispatch('setLoading', false)
        if (this.checkResponseHasErrorMessage(err, true)) {
          this.setErrors(err.response.data.errors)
        }
        this.handleApiError(err, this.$t(`msg["Delete failed"]`))
      }
    },
  },
}
</script>

