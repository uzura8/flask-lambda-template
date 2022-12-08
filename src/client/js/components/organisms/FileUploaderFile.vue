<template>
<div>
  <div class="upload-file-box">
    <div
      v-if="isFileObject === true"
      class="has-text-weight-semibold"
    >{{ file.name }}</div>
    <div
      v-else
      class="has-text-weight-semibold"
      v-text="file.originalName ? file.originalName : file.fileId"
    ></div>

    <p
      v-if="file.size"
      class="is-size-6"
    >{{ file.size | formatBytes }}</p>

    <button
      class="button is-light is-small btn-delete"
      @click="deleteFile"
    >
      <span class="icon">
        <i class="fas fa-times-circle"></i>
      </span>
    </button>
  </div>

  <div
    v-if="error"
    class="has-text-danger"
  >{{ error }}</div>
  <div
    v-else-if="file.isUploaded"
    class="has-text-success"
  >Uploaded</div>

  <div
    v-if="enableCaption && isFileObject === false"
    class="mt-3"
  >
    <b-field
      :label="$t('common.dispLabel')"
      label-position="inside"
    >
      <b-input
        v-model="caption"
        @blur="inputCaption"
      ></b-input>
    </b-field>
  </div>

  <div
    v-if="isFileObject === false"
    class="mt-3"
  >
    <div class="mt-2">
      <button
        class="button"
        @click="copyUrl()"
      >
        <span class="icon">
          <i v-if="actionButtonType === 'copy'" class="fas fa-copy"></i>
          <i v-else class="fas fa-plus"></i>
        </span>
        <span v-if="actionButtonType === 'copy'">{{ $t('common.copyFor', { target: 'URL' }) }}</span>
      </button>
    </div>
  </div>
  <b-loading :is-full-page="false" v-model="isUploading"></b-loading>
</div>
</template>
<script>
import axios from 'axios'
import { Admin } from '@/api'
import config from '@/config/config'
import util from '@/util'
import EbDropdown from '@/components/molecules/EbDropdown'

export default{
  name: 'FileUploaderFile',

  components: {
    EbDropdown,
  },

  props: {
    file: {
      type: null,
    },

    enableCaption: {
      type: Boolean,
      default: false,
    },

    actionButtonType: {
      type: String,
      required: false,
      default: 'copy',
    },
  },

  data(){
    return {
      WINDOW_URL: null,
      uploaderOptions: null,
      isUploading: false,
      caption: '',
      error: '',
    }
  },

  computed: {
    isFileObject() {
      return this.file instanceof File
    },

    //sizes() {
    //  return config.media.upload.image.sizes
    //},
  },

  watch: {
    //file(val) {
    //}
  },

  created() {
    this.WINDOW_URL = (window.URL || window.webkitURL)
    this.uploaderOptions = config.media.upload.file
  },

  async mounted() {
    if (this.file.caption) this.caption = this.file.caption
    if (this.isFileObject) {
      //this.setThumbToLocalImage()
      await this.upload()
    }
  },

  destroyed() {
    this.WINDOW_URL.revokeObjectURL(this.file)
  },

  methods: {
    async deleteFile() {
      if (this.isFileObject || this.file.isSaved) {
        this.$emit('delete-file', this.file.fileId)
        return
      }
      try {
        this.isUploading = true
        const res = await Admin.deleteFile(this.serviceId, this.file.fileId, this.adminUserToken)
        this.isUploading = false
        this.$emit('delete-file', this.file.fileId)
      } catch (err) {
        console.log(err)//!!!!!!
        this.error = this.$t('msg["Delete failed"]')
        this.isUploading = false
      }
    },

    async upload() {
      this.validate()
      if (this.error) return

      const reserved = await this.createS3PreSignedUrl()
      if (!reserved) return

      this.file.fileId = reserved.fileId
      const emitData = { fileId:reserved.fileId, mimeType:reserved.mimeType }

      const res = await this.uploadToS3(reserved.url)
      if (!res) return

      this.$emit('uploaded-file', emitData)
    },

    async createS3PreSignedUrl() {
      try {
        let vals = {
          fileId: this.file.fileId,
          fileType: 'file',
          mimeType: this.file.type,
          name: this.file.name,
          size: this.file.size,
        }
        this.isUploading = true
        const res = await Admin.createS3PreSignedUrl(this.serviceId, vals, this.adminUserToken)
        this.isUploading = ''
        return res
      } catch (err) {
        console.log(err);//!!!!!!
        this.isUploading = false
        this.error = this.$t('msg["Upload failed"]')
      }
    },

    async uploadToS3(url) {
      try {
        this.isUploading = true
        const res = await axios({
          method: 'PUT',
          url: url,
          headers: {'Content-Type': this.file.type},
          data: this.file
        })
        this.isUploading = false
        return res
      } catch (err) {
        console.log(err);//!!!!!!
        this.isUploading = false
        this.error = this.$t('msg["Upload failed"]')
      }
    },

    inputCaption(event) {
      const emitData = { fileId:this.file.fileId, caption:this.caption }
      this.$emit('input-caption', emitData)
    },

    copyUrl() {
      const fileUrl = this.mediaUrl('file', this.file.fileId, this.file.mimeType)
      this.$emit('copy-url', { url:fileUrl, caption:this.caption })
    },

    validate() {
      if (util.str.checkExtension(this.file.name, this.getUploadConfig('extensions')) === false) {
        this.error = this.$t('msg.invalidError', { field: this.$t('common.extention') })
        return
      }

      const mimeTypes = this.getUploadConfig('mimeTypes', [])
      if (mimeTypes && mimeTypes.includes(this.file.type) === false) {
        this.error = this.$t('msg.invalidError', { field: this.$t('common.fileType') })
        return
      }

      const sizeLimit = this.getUploadConfig('size', 0)
      if (sizeLimit && this.file.size > sizeLimit) {
        this.error = this.$t('msg.overMaxSizeOnUpload', { max: util.str.bytesFormat(sizeLimit) })
        return
      }
    },

    getUploadConfig(key, defaultVal) {
      if (key === 'size') {
        return Number(this.uploaderOptions.sizeLimitMB) * 1024 * 1024
      }
      if (key in this.uploaderOptions) {
        return this.uploaderOptions[key]
      }
      return defaultVal
    },
  },
}
</script>
<style scoped>
.upload-file-box {
  position: relative;
  padding-right: 20px;
}
.btn-delete {
  position: absolute;
  top: 0;
  right: 0;
}
</style>
