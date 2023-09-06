<template>
<div v-if="post">

  <b-message
    v-if="post.postStatus !== 'publish'"
    type="is-danger"
  >{{ $t('msg.thisIsUnpublished', {name: $t('common.post')}) }}</b-message>

  <b-message
    v-else-if="isPublished === false"
    type="is-warning"
  >{{ $t('msg.thisIsNotPublishedYet', {name: $t('common.post')}) }}</b-message>

  <b-message
    v-if="post.isHiddenInList === true"
  >{{ $t('msg.hiddenInList') }}</b-message>

  <div class="block">
    <router-link :to="postsPageUriObj">
      <i class="fas fa-chevron-left"></i>
      <span>{{ $t('common.posts') }}</span>
    </router-link>
  </div>

  <h1 class="title">
    <span
      v-if="isPublishItem === false"
      class="tag is-danger"
    >{{ $t('common.unpublished') }}</span>

    {{ post.title }}
  </h1>

  <div
    class="is-clearfix mb-4"
  >
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
            v-if="hasEditorRole"
            :to="`/admin/posts/${serviceId}/${post.postId}/edit`"
            class="dropdown-item"
          >
            <span class="icon">
              <i class="fas fa-pen"></i>
            </span>
            <span>{{ $t('common.edit') }}</span>
          </router-link>

          <a
            v-if="hasEditorRole && isPublishItem"
            @click="updateStatus(false)"
            class="dropdown-item is-clickable"
          >
            <span class="icon">
              <i class="fas fa-lock"></i>
            </span>
            <span>{{ $t('common.unpublish') }}</span>
          </a>

          <a
            v-else-if="hasEditorRole && !isPublishItem"
            @click="confirmPublish()"
            class="dropdown-item is-clickable"
          >
            <span class="icon">
              <i class="fas fa-globe"></i>
            </span>
            <span>{{ $t('common.publish') }}</span>
          </a>

          <a
            v-if="hasEditorRole"
            @click="openGroupSelectModal"
            class="dropdown-item is-clickable"
          >
            <span class="icon">
              <i class="far fa-star"></i>
            </span>
            <span>{{ $t('term.postGroup') }}</span>
          </a>

          <a
            v-if="hasEditorRole"
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

      <b-modal
        v-model="isGroupSelectModalActive"
        :destroy-on-hide="false"
        aria-role="dialog"
        close-button-aria-label="Close"
        aria-modal
        width="420px"
      >
        <template #default="props">
          <div class="modal-card" style="width: auto">
            <header class="modal-card-head">
              <p class="modal-card-title">
                {{ $t('term.postGroup') }}
              </p>
              <button
                type="button"
                class="delete"
                @click="isGroupSelectModalActive = false"
              ></button>
            </header>
            <section class="modal-card-body">
              <admin-post-groups-by-post
                :post-id="post.postId"
                @close="isGroupSelectModalActive = false"
              ></admin-post-groups-by-post>
            </section>
            <footer class="modal-card-foot">
              <button
                class="button"
                type="button"
                @click="isGroupSelectModalActive = false"
              >{{ $t('common.close') }}</button>
            </footer>
          </div>
        </template>
      </b-modal>
    </div>
    <div
      v-if="isEditablePostBody"
      class="is-pulled-left"
    >
      <span v-if="isEditPostBody === true">
        <button
          @click="updatePostBody()"
          :disabled="isEditedPostBodyFromLoaded === false"
          class="button is-warning is-small"
        >
          <span class="icon is-small">
            <i class="fas fa-save"></i>
          </span>
          <span>{{ $t('common.save') }}</span>
        </button>

        <button
          @click="cancelEditBody()"
          class="button is-small ml-3"
        >
          <span class="icon is-small">
            <i class="fas fa-undo"></i>
          </span>
          <span>{{ $t('common.cancel') }}</span>
        </button>
      </span>

      <button
        v-else
        @click="isEditPostBody = true"
        class="button is-small"
      >
        <span class="icon is-small">
          <i class="fas fa-pen"></i>
        </span>
        <span>{{ $t('common.editDirectly') }}</span>
      </button>
    </div>
  </div>

  <div v-if="isEditPostBody === true">
    <markdown-editor
      v-model="body"
      @blur="updatePostBody(false)"
    ></markdown-editor>
  </div>
  <div
    v-else
    class="mb-6"
  >
    <post-body-markdown
      v-if="post.bodyFormat === 'markdown'"
      :body="body"
    ></post-body-markdown>

    <post-body-json
      v-else-if="post.bodyFormat === 'json'"
      :body-json="post.bodyJson"
    ></post-body-json>

    <post-body
      v-else
      :body="post.bodyHtml"
    ></post-body>
  </div>

  <div
    v-if="checkObjHasProp(post, 'images', true)"
    class="content block mt-6"
  >
    <label class="has-text-weight-semibold mr-2">{{ $t('common.images') }}</label>
    <a
      class="u-clickable"
      @click="isImagesModalActive = true"
    >
      <span class="icon">
        <i class="fas fa-images"></i>
      </span>
      <span>{{ post.images.length }}</span>
    </a>
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
  </div>

  <div
    v-if="checkObjHasProp(post, 'files', true)"
    class="content block"
  >
    <h4 class="title is-6 mb-1">{{ $t('common.files') }}</h4>
    <ul class="mt-1">
      <li v-for="file in post.files">
        <a
          :href="mediaUrl('file', file.fileId, file.mimeType)"
          target="_blank"
          v-text="file.caption ? file.caption : file.fileId"
        ></a>
      </li>
    </ul>
  </div>

  <div
    v-if="checkObjHasProp(post, 'links', true)"
    class="content block"
  >
    <h4 class="title is-6 mb-1">{{ $t('common.links') }}</h4>
    <ul class="mt-1">
      <li v-for="link in post.links">
        <a
          :href="link.url"
          target="_blank"
          v-text="link.label ? link.label : link.url"
        ></a>
      </li>
    </ul>
  </div>

  <div
    v-if="checkObjHasProp(post, 'category', true)"
    class="content block"
  >
    <h4 class="title is-6 mb-1">{{ $t('common.category') }}</h4>
    <nav
      class="breadcrumb"
      aria-label="breadcrumbs"
    >
      <ul class="">
        <li
          v-if="checkObjHasProp(post.category, 'parents', true)"
          v-for="parent in post.category.parents"
        >
          <router-link :to="{
            path: `/admin/posts/${serviceId}`,
            query: { category: parent.slug }
          }">
            {{ parent.label }}
          </router-link>
        </li>
        <li>
          <router-link
            :to="{
              path: `/admin/posts/${serviceId}`,
              query: { category: post.category.slug }
          }">
            {{ post.category.label }}
          </router-link>
        </li>
      </ul>
    </nav>
  </div>

  <div
    v-if="checkObjHasProp(post, 'tags', true)"
    class="content block"
  >
    <h4 class="title is-6 mb-1">{{ $t('common.tags') }}</h4>
    <div>
      <span
        v-for="tag in post.tags"
        class="tag ml-2"
      >
        {{ tag.label }}
      </span>
    </div>
  </div>

  <ul class="block mt-4">
    <li>
      <label class="has-text-weight-semibold mr-2">{{ $t('common.publishAt') }}</label>
      <inline-time
        :time-class="isReserved ? 'has-text-warning-dark' : ''"
        :datetime="post.publishAt"
      ></inline-time>
      <span v-if="isReserved" class="tag is-warning">{{ $t('common.reserved') }}</span>
    </li>
    <li>
      <label class="has-text-weight-semibold mr-2">{{ $t('common.createdAt') }}</label>
      <inline-time :datetime="post.createdAt"></inline-time>
    </li>
    <li>
      <label class="has-text-weight-semibold mr-2">{{ $t('common.lastUpdatedAt') }}</label>
      <inline-time :datetime="post.updatedAt"></inline-time>
    </li>
  </ul>
</div>
</template>
<script>
import { Admin } from '@/api'
import config from '@/config/config'
import obj from '@/util/obj'
import PostBody from '@/components/atoms/PostBody'
import PostBodyJson from '@/components/atoms/PostBodyJson'
import PostBodyMarkdown from '@/components/atoms/PostBodyMarkdown'
import InlineTime from '@/components/atoms/InlineTime'
import EbDropdown from '@/components/molecules/EbDropdown'
import MarkdownEditor from '@/components/atoms/MarkdownEditor'
import FbImg from '@/components/atoms/FbImg'
import AdminPostGroupsByPost from '@/components/organisms/AdminPostGroupsByPost'

export default{
  name: 'AdminPost',

  components: {
    InlineTime,
    EbDropdown,
    PostBody,
    PostBodyJson,
    PostBodyMarkdown,
    MarkdownEditor,
    FbImg,
    AdminPostGroupsByPost,
  },

  data(){
    return {
      post: null,
      isImagesModalActive: false,
      isEditPostBody: false,
      body: '',
      bodyLastPosted: '',
      isGroupSelectModalActive: false,
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

    postsPageUriObj() {
      const path = `/admin/posts/${this.serviceId}`
      const query = this.$store.getters.adminPostsPagerQueryCurrent(true)
      return { path:path, query:query }
    },

    previewUrl() {
      if (!this.post) return ''
      if (obj.checkObjHasProp(this.post, 'service') === false) return ''
      if (obj.checkObjHasProp(this.post.service, 'configs') === false) return ''
      if (obj.checkObjHasProp(this.post.service.configs, 'frontendPostDetailUrlPrefix') === false) return ''

      const previewUrlPrefix = this.post.service.configs.frontendPostDetailUrlPrefix
      const previewUrl = `${previewUrlPrefix}${this.post.slug}`
      if (this.isPublished) return previewUrl

      if (this.checkEmpty(this.post.previewToken)) return ''
      const delimitter = previewUrl.indexOf('?') === -1 ? '?' : '&'
      return `${previewUrl}${delimitter}token=${this.post.previewToken}`
    },

    isEditablePostBody() {
      if (this.checkObjHasProp(config.post, 'isEditablePostBodyOnPageByMarkdown', true) === false) {
        return false
      }
      if (this.hasEditorRole === false) return false
      return this.post.bodyFormat === 'markdown'
    },

    isEditedPostBodyFromLoaded() {
      return this.body !== this.post.body
    },

    isEditedPostBodyFromLastPost() {
      return this.body !== this.bodyLastPosted
    },

    formattedBodyJson() {
      if (this.post.bodyFormat !== 'json') return ''
      return JSON.stringify(this.post.bodyJson, null, "  ").trim()
    },
  },

  async created() {
    await this.setPost()
  },

  methods: {
    async setPost() {
      this.$store.dispatch('setLoading', true)
      try {
        this.post = await Admin.getPosts(this.serviceId, this.postId, null, this.adminUserToken)
        this.body = this.post.body
        this.bodyLastPosted = this.body
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, 'Failed to get data from server')
      }
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
        await this.checkAndRefreshTokens()
        const postStatus = isPublish ? 'publish' : 'unpublish'
        const res = await Admin.updatePostStatus(this.serviceId, this.postId, postStatus, this.adminUserToken)
        this.$store.dispatch('setAdminPostList', null)
        this.$store.dispatch('setLoading', false)
        this.post = res
        this.$emit('posted', res)
        this.showGlobalMessage(this.$t('msg.changePublishStatusCompleted'), 'is-success')
      } catch (err) {
        this.debugOutput(err)
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

    async updatePostBody(isFinishEdit = true) {
      try {
        await this.checkAndRefreshTokens()
        this.body = this.body.trimEnd()
        if (this.isEditedPostBodyFromLastPost === true) {
          this.$store.dispatch('setLoading', true)
          const vals = { body: this.body, bodyFormat: this.post.bodyFormat }
          await Admin.updatePost(this.serviceId, this.post.postId, vals, this.adminUserToken)
          this.bodyLastPosted = this.body
          this.$store.dispatch('setLoading', false)
        }
        if (isFinishEdit === true) this.isEditPostBody = false
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        if (this.checkResponseHasErrorMessage(err, true)) {
          this.setErrors(err.response.data.errors)
        }
        this.handleApiError(err, this.$t(`msg["Update failed"]`))
      }
    },

    async cancelEditBody() {
      this.body = this.post.body
      await this.updatePostBody()
      this.isEditPostBody = false
    },

    async deletePost() {
      try {
        this.$store.dispatch('setLoading', true)
        await this.checkAndRefreshTokens()
        const res = await Admin.deletePost(this.serviceId, this.postId, this.adminUserToken)
        this.$store.dispatch('setAdminPostList', null)
        this.$store.dispatch('setLoading', false)
        this.$router.push(`/admin/posts/${this.serviceId}`)
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        if (this.checkResponseHasErrorMessage(err, true)) {
          this.setErrors(err.response.data.errors)
        }
        this.handleApiError(err, this.$t(`msg["Delete failed"]`))
      }
    },

    async openGroupSelectModal() {
      this.isGroupSelectModalActive = true
    },
  },
}
</script>

