<template>
<div class="flex-item">
  <b-field
    :label="$t('form.slug')"
    :type="checkEmpty(errors.slug) ? '' : 'is-danger'"
    :message="checkEmpty(errors.slug) ? '' : errors.slug[0]"
  >
    <b-input
      v-model="slug"
      @blur="validate('slug')"
      expanded
    ></b-input>
    <div
      v-if="isEnableSlugAutoSetButton"
      class="controll"
    >
      <eb-dropdown
        position="is-bottom-left"
      >
        <span slot="label">{{ $t('term.autoInput') }}</span>
        <div class="dropdown-content">
          <a
            class="dropdown-item"
            @click="setSlug('date')"
          >{{ $t('common.date') }}
          </a>
          <a
            class="dropdown-item"
            @click="setSlug('randString')"
          >{{ $t('term.randString') }}
          </a>
        </div>
      </eb-dropdown>
    </div>
  </b-field>

  <b-field
    :label="$t('common.category')"
    :type="checkEmpty(errors.category) ? '' : 'is-danger'"
    :message="checkEmpty(errors.category) ? '' : errors.category[0]"
    class="mt-6"
  >
    <category-select
      v-model="category"
    ></category-select>
  </b-field>

  <b-field
    :label="$t('form.title')"
    :type="checkEmpty(errors.title) ? '' : 'is-danger'"
    :message="checkEmpty(errors.title) ? '' : errors.title[0]"
    class="mt-6"
  >
    <b-input
      v-model="title"
      @blur="validate('title')"
    ></b-input>
  </b-field>
  <b-field
    :label="$t('form.body')"
    :message="checkEmpty(errors.editorModeOption) ? '' : errors.editorModeOption[0]"
    class="mt-6"
  >
    <b-select v-model="editorMode">
      <option
        v-for="editorMode in editorModes"
        :value="editorMode.mode"
        v-text="$t(`term['${editorMode.mode}']`)"
        :disabled="editorMode.mode === 'richText' && isEnabledRichText === false"
      ></option>
    </b-select>
  </b-field>

  <b-field
    :type="checkEmpty(errors.body) ? '' : 'is-danger'"
    :message="checkEmpty(errors.body) ? '' : errors.body[0]"
  >
    <rich-text-editor
      v-if="isEnabledRichText && editorMode === 'richText'"
      v-model="body"
    ></rich-text-editor>

    <markdown-editor
      v-else-if="editorMode === 'markdown'"
      v-model="body"
    ></markdown-editor>

    <v-jsoneditor
      v-model="body"
      v-else-if="editorMode === 'json'"
      height="500px"
      @error="handleJsonEditorError"
      :options=jsonEditorOptions
      :plus="false"
    />

    <b-input
      v-else
      type="textarea"
      v-model="body"
      @blur="validate('body')"
      ref="inputBody"
    ></b-input>
  </b-field>

  <b-field
    :label="$t('common.images')"
    :type="checkEmpty(errors.images) ? '' : 'is-danger'"
    :message="checkEmpty(errors.images) ? '' : $t('msg.ErrorsExist')"
    class="mt-6"
  >
    <file-uploader
      v-if="uploaderOptions"
      file-type="image"
      v-model="images"
      :image-action-button-type="editorMode === 'markdown' ? 'copy' : 'insert'"
      :uploader-options="uploaderOptions.image"
      @insert-image="insertImage"
    ></file-uploader>
  </b-field>

  <b-field
    :label="$t('form.files')"
    :type="checkEmpty(errors.files) ? '' : 'is-danger'"
    :message="checkEmpty(errors.files) ? '' : $t('msg.ErrorsExist')"
    class="mt-6"
  >
    <file-uploader
      v-if="uploaderOptions"
      file-type="file"
      v-model="files"
      :uploader-options="uploaderOptions.file"
      @copy-url="copyUrl"
    ></file-uploader>
  </b-field>

  <b-field
    :label="$t('common.link')"
    :type="checkEmpty(errors.links) ? '' : 'is-danger'"
    :message="checkEmpty(errors.links) ? '' : $t('msg.ErrorsExist')"
    class="mt-6"
  >
    <ul v-if="links.length > 0">
      <li
        v-for="link in links"
        :key="link.id"
      >
        <link-inputs
          :link="link"
          @updated-link="updateLink"
          @delete="deleteLink"
          @has-error="setLinksError"
        ></link-inputs>
      </li>
    </ul>
  </b-field>
  <b-field>
    <button
      @click="addLink"
      class="button"
      :disabled="isAddLinkBtnEnabled === false"
    >
      <span class="icon">
        <i class="fas fa-link"></i>
      </span>
      <span>{{ $t('common.addFor', { target: $t('common.link') }) }}</span>
    </button>
  </b-field>

  <b-field
    :label="$t('common.tag')"
    :type="checkEmpty(errors.tags) ? '' : 'is-danger'"
    :message="checkEmpty(errors.tags) ? $t('form.ExpAboutNewTagsSeparater') : errors.tags[0]"
    class="mt-6"
  >
    <b-taginput
      v-model="tags"
      :data="filteredTags"
      :autocomplete="true"
      :allow-new="true"
      :open-on-focus="true"
      field="label"
      icon-pack="fas"
      icon="tag"
      placeholder=""
      @typing="getFilteredTags"
    ></b-taginput>
  </b-field>

  <b-field
    :label="$t('common.publishAt')"
    :type="checkEmpty(errors.publishAt) ? '' : 'is-danger'"
    :message="checkEmpty(errors.publishAt) ? '' : errors.publishAt[0]"
    class="mt-6"
  >
    <b-datetimepicker
      v-model="publishAt"
      @blur="validate('publishAt')"
      locale="ja-JP"
      icon-pack="fas"
      icon="calendar-day"
      editable
    >
      <template #left>
        <b-button
          label="Now"
          type="is-primary"
          icon-left="clock"
          icon-pack="fas"
          @click="publishAt = new Date()"
        ></b-button>
      </template>

      <template #right>
        <b-button
          label="Clear"
          type="is-danger"
          icon-left="times"
          icon-pack="fas"
          outlined
          @click="publishAt = null"
        ></b-button>
      </template>
    </b-datetimepicker>
  </b-field>

  <b-field
    :label="$t('common.dispSetting')"
    :type="checkEmpty(errors.isHiddenInList) ? '' : 'is-danger'"
    :message="checkEmpty(errors.isHiddenInList) ? '' : errors.isHiddenInList[0]"
    class="mt-6"
  >
    <b-checkbox v-model="isHiddenInList">
      {{ $t('form.hideInList') }}
    </b-checkbox>
  </b-field>

  <div
    v-if="globalError"
    class="block has-text-danger mt-6"
  >{{ globalError }}</div>

  <div class="field mt-6">
    <div
      v-if="!isPublished"
      class="control"
    >
      <button
        class="button is-info"
        :disabled="isLoading || hasErrors"
        @click="save(false)"
        v-text="$t('common.saveDraft')"
      ></button>
    </div>

    <div
      v-else
      class="control"
    >
      <button
        class="button is-warning"
        :disabled="isLoading || hasErrors"
        @click="save(false)"
        v-text="$t('common.edit')"
      ></button>
    </div>
  </div>

  <div class="field">
    <div
      v-if="!isPublished"
      class="control"
    >
      <button
        class="button is-warning"
        :disabled="isLoading || hasErrors"
        @click="save(true)"
        v-text="$t('common.publish')"
      ></button>
    </div>
  </div>

  <div class="field">
    <div class="control">
      <button
        class="button is-light"
        :disabled="isLoading"
        @click="cancel"
        v-text="$t('common.cancel')"
      ></button>
    </div>
  </div>
</div>
</template>
<script>
//import tinymce from 'tinymce'
import { getTinymce } from '@tinymce/tinymce-vue/lib/cjs/main/ts/TinyMCE'
import VJsoneditor from 'v-jsoneditor'
import str from '@/util/str'
import obj from '@/util/obj'
import utilDate from '@/util/date'
import utilMedia from '@/util/media'
import { Admin, Category, Tag } from '@/api'
import config from '@/config/config'
import RichTextEditor from '@/components/atoms/RichTextEditor'
import MarkdownEditor from '@/components/atoms/MarkdownEditor'
import FileUploader from '@/components/organisms/FileUploader'
import LinkInputs from '@/components/molecules/LinkInputs'
import CategorySelect from '@/components/molecules/CategorySelect'
import EbDropdown from '@/components/molecules/EbDropdown'

export default{
  name: 'AdminPostForm',

  components: {
    FileUploader,
    LinkInputs,
    RichTextEditor,
    MarkdownEditor,
    CategorySelect,
    EbDropdown,
    VJsoneditor,
  },

  props: {
    post: {
      type: Object,
      default: null,
    },
  },

  data(){
    return {
      slug: '',
      category: '',
      title: '',
      images: [],
      files: [],
      links: [],
      body: '',
      editorMode: '',
      tags: [],
      publishAt: null,
      isHiddenInList: false,
      fieldKeys: ['slug', 'category', 'title', 'images', 'files', 'links', 'editorMode', 'body', 'tags', 'publishAt', 'isHiddenInList'],
      savedTags: [],
      filteredTags: [],
      errors: [],
      uploaderOptions: null,
      editorModes: [
        {
          mode: 'richText',
          format: 'html',
        },
        {
          mode: 'markdown',
          format: 'markdown',
        },
        {
          mode: 'text',
          format: 'text',
        },
        {
          mode: 'rawHtml',
          format: 'html',
        },
        {
          mode: 'json',
          format: 'json',
        },
      ],
      jsonEditorOptions: {
        mode: 'code',
        onEditable: function (node) {
          return true;
        }
      }
    }
  },

  computed: {
    isEdit() {
      return this.post != null
    },

    isPublished() {
      if (this.isEdit === false) return false
      return this.post.postStatus === 'publish'
    },

    categoryQuery() {
      const defaultValue = ''
      if (!this.$route.query.category) return defaultValue
      return this.$route.query.category
    },

    isAddLinkBtnEnabled() {
      if (this.checkEmpty(this.errors.links) === false) return false
      if (this.checkEmpty(this.links)) return true
      for (let i = 0, n = this.links.length; i < n; i++) {
        if (this.links[i].url.length === 0) return false
      }
      return true
    },

    isEmptyRequiredFields() {
      if (!this.checkEmpty(this.slug)) return false
      if (!this.checkEmpty(this.title)) return false
      return true
    },

    hasErrors() {
      if (this.globalError) return true

      let hasError = false
      Object.keys(this.errors).map(field => {
        if (this.errors[field].length > 0) hasError = true
      })
      return hasError
    },

    isEnabledRichText() {
      return Boolean(config.tinyMCEApiKey)
    },

    bodyFormat() {
      return this.getFormatByMode(this.editorMode)
    },

    isEnableSlugAutoSetButton() {
      return obj.getVal(config.post, 'isEnableSlugAutoSetButton', false)
    },

    postsPageUriObj() {
      const path = `/admin/posts/${this.serviceId}`
      const query = this.$store.getters.adminPostsPagerQueryCurrent(true)
      return { path:path, query:query }
    },
  },

  watch: {
    tags(val) {
      this.updateFilteredTags()
      this.validate('tags')
    },

    images(vals) {
      this.initError('images')
    },

    files(vals) {
      this.initError('files')
    },

    links(vals) {
      this.initError('links')
    },

    body(vals) {
      if (this.bodyFormat === 'json') {
        this.initError('body')
      }
    },

    editorMode(val, oldVal) {
      if (!oldVal) return
      this.setBody()
    },
  },

  async created() {
    this.setEditorMode()
    if (this.isEnabledRichText === false) this.editorMode = 'text'
    if (this.isEdit === true) {
      this.setPost()
    } else {
      if (this.categoryQuery) {
        this.category = this.categoryQuery
      }
      if (config.post.autoSlugSet.isEnabled === true) {
        await this.setSlug(config.post.autoSlugSet.format)
      }
    }
    await this.setTags()
    await this.setUploaderOptions()
  },

  methods: {
    setEditorMode() {
      this.editorMode = 'richText'
      if (this.checkObjHasProp(config.post, 'defaultEditorMode', true)) {
        this.editorMode = config.post.defaultEditorMode
      }
      if (this.editorMode === 'richText' && this.isEnabledRichText === false) {
        this.editorMode = 'text'
      }
    },

    setPost() {
      this.slug = this.post.slug != null ? String(this.post.slug) : ''
      this.category = ('category' in this.post && this.post.category && this.post.category.slug != null)
        ? String(this.post.category.slug)
        : ''
      this.title = this.post.title != null ? String(this.post.title) : ''
      this.images = this.post.images != null ? this.post.images : []
      this.files = this.post.files != null ? this.post.files : []
      this.links = this.post.links != null ? this.post.links : []
      this.editorMode = this.getModeByFormat(this.post.bodyFormat)
      if (this.post.bodyFormat === 'json') {
        this.body = this.post.body != null ? JSON.parse(this.post.body) : {}
      } else {
        this.body = this.post.body != null ? String(this.post.body) : ''
      }
      this.tags = this.checkEmpty(this.post.tags) === false ? this.post.tags : []
      this.publishAt = this.post.publishAt && this.post.publishAt !== 'None' ? new Date(this.post.publishAt) : null
      this.isHiddenInList = this.post.isHiddenInList
    },

    setBody() {
      const defBody = this.isEdit ? this.post.body : ''
      if (this.bodyFormat === 'json' && typeof this.body === 'string') {
        this.body = str.checkJson(this.body) ? JSON.parse(this.body) : {}
      } else if (this.bodyFormat !== 'json' && typeof this.body !== 'string') {
        this.body = defBody
      }
    },

    async setSlug(format) {
      this.initError('slug')
      try {
        let slug
        let isNotExists = false

        for (let i = 0, n = 10; i < n; i++) {
          if (isNotExists === true) break

          if (format === 'randString') {
            slug = str.getRandStr(11)
          } else {
            slug = this.getSlugAsDateFormat(slug)
          }
          isNotExists = await this.checkSlugNotExists(slug)
        }
        if (isNotExists === false) {
          throw new Error('Create Slug Failed')
        }
        this.slug = slug
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    async setTags() {
      try {
        const res = await Tag.getAll(this.serviceId)
        if (res.length > 0) {
          this.savedTags = res
          this.filteredTags = res
        }
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    async setUploaderOptions() {
      try {
        const res = await Admin.getServices(this.serviceId, null, this.adminUserToken)
        this.uploaderOptions = {
          image: {
            sizes: res.configs.mediaUploadImageSizes,
            mimeTypes: res.configs.mediaUploadAcceptMimetypesImage,
            extensions: [],
            sizeLimitMB: res.configs.mediaUploadSizeLimitMBImage,
          },
          file: {
            mimeTypes: res.configs.mediaUploadAcceptMimetypesFile,
            extensions: [],
            sizeLimitMB: res.configs.mediaUploadSizeLimitMBFile,
          },
        }
        res.configs.mediaUploadAcceptMimetypesImage.map((item) => {
          let ext = utilMedia.getExtensionByMimetype(item)
          this.uploaderOptions.image.extensions.push(ext)
        })
        res.configs.mediaUploadAcceptMimetypesFile.map((item) => {
          let ext = utilMedia.getExtensionByMimetype(item)
          this.uploaderOptions.image.extensions.push(ext)
        })
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    resetInputs() {
      this.slug = ''
      this.category = ''
      this.title = ''
      if (this.editorMode !== 'richText') {
        this.body = ''
      }
      this.images = []
      this.files = []
      this.links = []
      this.tags = []
      this.publishAt = null
      this.isHiddenInList = false
    },

    async save(forcePublish = false) {
      this.validateAll()
      if (this.hasErrors) return

      try {
        let vals = {}
        vals.slug = this.slug
        vals.category = this.category
        vals.title = this.title
        vals.bodyFormat = this.bodyFormat
        vals.images = this.images
        vals.files = this.files
        vals.links = this.links
        vals.isHiddenInList = this.isHiddenInList
        if (this.bodyFormat === 'json') {
          vals.body = JSON.stringify(this.body)
        } else {
          vals.body = this.body
        }

        vals.tags = []
        this.tags.map((tag) => {
          if (typeof tag === 'string') {
            vals.tags.push({ label: tag })
          } else {
            vals.tags.push({ tagId: tag.tagId })
          }
        })

        if (this.publishAt) {
          vals.publishAt = utilDate.utcDateStrFromJsDate(this.publishAt)
        }
        if (forcePublish) {
          vals.status = 'publish'
        } else {
          if (this.isEdit === false) vals.status = 'unpublish'
        }
        this.$store.dispatch('setLoading', true)
        await this.checkAndRefreshTokens()
        let res
        if (this.isEdit) {
          res = await Admin.updatePost(this.serviceId, this.post.postId, vals, this.adminUserToken)
        } else {
          res = await Admin.createPost(this.serviceId, vals, this.adminUserToken)
          this.$store.dispatch('resetAdminPostsPager', false)
        }
        this.$store.dispatch('setAdminPostList', null)
        this.$store.dispatch('setLoading', false)
        this.$emit('posted', res)
        this.resetInputs()
        this.$router.push(`/admin/posts/${this.serviceId}/${res.postId}`)
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        if (this.checkResponseHasErrorMessage(err, true)) {
          this.setErrors(err.response.data.errors)
        }
        const msgKey = this.isEdit ? 'Edit failed' : 'Create failed'
        this.handleApiError(err, this.$t(`msg["${msgKey}"]`))
      }
    },

    async checkSlugNotExists(slug) {
      try {
        this.$store.dispatch('setLoading', true)
        await this.checkAndRefreshTokens()
        const res = await Admin.checkPostSlugNotExists(this.serviceId, slug, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
        return res
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err)
      }
    },

    cancel() {
      this.resetInputs()
      this.$router.push(this.postsPageUriObj)
    },

    handleJsonEditorError(ev) {
      this.initError('body')
      this.errors.body.push(this.$t('msg.ErrorsExist'))
      // console.log(ev)
    },

    validateAll() {
      this.fieldKeys.map(field => {
        this.validate(field)
      })
      if (this.hasErrors) {
        this.globalError = this.$t("msg['Correct inputs with error']")
      } else if (this.isEmptyRequiredFields) {
        this.globalError = this.$t("msg['Input required']")
      }
    },

    validate(field) {
      const key = 'validate' + str.capitalize(field)
      this[key]()
    },

    async validateSlug() {
      this.initError('slug')
      if (this.slug === null) this.slug = ''
      this.slug = this.slug.trim()
      if (this.checkEmpty(this.slug)) {
        this.errors.slug.push(this.$t('msg["Input required"]'))
      } else if (str.checkSlug(this.slug, true) === false) {
        this.errors.slug.push(this.$t('msg.InvalidInput'))
      } else if (this.isEdit === false || this.slug !== this.post.slug) {
        const isNotExists = await this.checkSlugNotExists(this.slug)
        if (isNotExists === false) {
          this.errors.slug.push(this.$t('msg["Already in use"]'))
        }
      }
    },

    async validateCategory() {
      this.initError('category')
      if (this.category === null) this.category = ''
      this.category = this.category.trim()
      if (!this.checkEmpty(this.category) && str.checkSlug(this.category) === false) {
        this.errors.category.push(this.$t('msg.InvalidInput'))
      }
    },

    validateTitle() {
      this.initError('title')
      if (this.title === null) this.title = ''
      this.title = this.title.trim()
      if (this.checkEmpty(this.title)) this.errors.title.push(this.$t('msg["Input required"]'))
    },

    validateBody() {
      this.initError('body')
      if (this.body === null) {
        if (this.bodyFormat === 'json') {
          this.body = {}
        } else {
          this.body = ''
        }
      }
      if (this.bodyFormat !== 'json') this.body = this.body.trimEnd()
      //if (this.checkEmpty(this.body)) this.errors.body.push(this.$t('msg["Input required"]'))
    },

    validateImages() {
      this.initError('images')
      if (this.images === null) this.images = []
    },

    validateFiles() {
      this.initError('files')
      if (this.files === null) this.files = []
    },

    validateLinks() {
      this.initError('links')
      if (this.links === null) this.links = []
      if (this.links.length > 0) {
        for (let i = 0, n = this.links.length; i < n; i++) {
          if (this.checkEmpty(this.links[i].url)) {
            if (this.checkEmpty(this.links[i].label)) {
              this.links.splice(i, 1)
            } else {
              this.errors.links.push('hasError')
            }
          }
        }
      }
    },

    validateEditorMode() {
      this.initError('editorMode')
      if (this.checkEmpty(this.editorMode)) {
        this.errors.editorMode.push(this.$t('msg["Input required"]'))
      } else if (this.editorModes.find(item => item.mode === this.editorMode) == null) {
        this.errors.editorMode.push(this.$t('msg.InvalidInput'))
      }
    },

    validateTags() {
      this.initError('tags')
      this.tags.map((val) => {
        if (typeof val !== 'string') return
        if (this.savedTags.find(saved => saved.label === val) != null) {
          this.errors.tags.push(this.$t('msg.duplicated'))
        }
      })
    },

    validatePublishAt() {
      this.initError('publishAt')
    },

    validateIsHiddenInList() {
      this.initError('isHiddenInList')
    },

    insertImage(payload) {
      const imgUrl = payload.url
      let imgTag
      if (this.editorMode === 'markdown') {
        const altText = payload.caption ? payload.caption : this.$t('common.image')
        imgTag = `![${altText}](${imgUrl})`
      } else if (this.editorMode === 'text') {
        imgTag = imgUrl
      } else {
        let attrs = ['img', `src="${imgUrl}"`]
        if (payload.caption) attrs.push(`alt="${payload.caption}"`)
        imgTag = '<' + attrs.join(' ') + '>'
      }

      if (['text', 'rawHtml'].includes(this.editorMode)) {
        const inputEl = this.$refs.inputBody.$el.getElementsByTagName('textarea')[0]
        const inputPos = inputEl.selectionStart
        const preVal = this.body.substr(0, inputPos)
        const postVal = this.body.substr(inputPos)
        this.body = `${preVal}${imgTag}${postVal}`
      } else if (this.editorMode === 'richText') {
        getTinymce().activeEditor.insertContent(imgTag)
      } else if (this.editorMode === 'markdown') {
        this.$copyText(imgTag)
          .then((e) => {
            this.$buefy.toast.open({
              message: this.$t('msg.copied'),
              type: 'is-success',
              position: 'is-bottom',
            })
          }, (e) => {
            this.$buefy.toast.open({
              message: this.$t('msg.copyFailed'),
              type: 'is-danger',
              position: 'is-bottom',
            })
          })
      } else {
        this.body += `\n${imgTag}`
      }
    },

    copyUrl(payload) {
      const fileUrl = payload.url
      this.$copyText(fileUrl)
        .then((e) => {
          this.$buefy.toast.open({
            message: this.$t('msg.copied'),
            type: 'is-success',
            position: 'is-bottom',
          })
        }, (e) => {
          this.$buefy.toast.open({
            message: this.$t('msg.copyFailed'),
            type: 'is-danger',
            position: 'is-bottom',
          })
        })
    },

    addLink() {
      let maxId = 0
      if (this.links.length > 0) {
        maxId = this.links.reduce((a, b) => a.id > b.id ? a : b).id
      }
      this.links.push({ id:maxId + 1, url:'', label:'' })
    },

    setLinksError(hasError) {
      if (hasError === false) {
        this.errors.links = []
      } else {
        this.errors.links.push('hasError')
      }
    },

    updateLink(payload) {
      const index = this.links.findIndex((item) => {
        return item.id === payload.id
      })
      this.links.splice(index, 1, payload)
    },

    deleteLink(id) {
      const index = this.links.findIndex((item) => {
        return item.id === id
      })
      this.links.splice(index, 1)
    },

    updateFilteredTags() {
      this.filteredTags = this.savedTags.filter((savedTag) => {
        const matched = this.tags.find((tag) => {
          if (typeof tag === 'string') {
            return tag === savedTag.label
          } else {
            return tag.label === savedTag.label
          }
        })
        return matched == null
      })
    },

    getFilteredTags(text) {
      this.filteredTags = this.savedTags.filter((option) => {
        if (this.tags.find(tag => tag.tagId == option.tagId) != null) return
        return option.label
          .toString()
          //.toLowerCase()
          //.indexOf(text.toLowerCase()) >= 0
          .indexOf(text) >= 0
      })
    },

    getModeByFormat(format) {
      const res = this.editorModes.find(item => item.format === format)
      if (res == null) return ''
      return res.mode
    },

    getFormatByMode(mode) {
      const res = this.editorModes.find(item => item.mode === mode)
      if (res == null) return ''
      return res.format
    },

    getSlugAsDateFormat(current) {
      const suffixes = 'abcdefghijklmnopqrstuvwxyz'.split('')
      const today = utilDate.currentStr('yyMMdd')
      if (!current) return today
      if (current === today) return today + suffixes[0]

      let currentSuffix = current.replace(today, '')
      const index = suffixes.indexOf(currentSuffix)
      if (index === -1) {
        throw new Error('Current slug is invalid')
      } else if (index + 1 > suffixes.length - 1) {
        throw new Error('Create Slug Failed')
      }
      return today + suffixes[index + 1]
    },
  },
}
</script>
<style>
.flex-item { flex:1; }
</style>
