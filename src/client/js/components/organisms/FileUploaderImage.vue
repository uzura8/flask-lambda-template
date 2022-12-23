<template>
<div class="upload-image-box">
  <div v-if="isFileObject" class="image">
    <img
      v-if="'thumb' in file && file.thumb"
      :src="file.thumb"
    />
    <span v-else>No Image</span>
  </div>
  <div v-else class="image">
    <fb-img
      :fileId="file.fileId"
      :mimeType="file.mimeType"
      size="raw"
    />
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
      :label="$t('common.caption')"
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
    <b-select v-model="insertSize">
      <option
        value="raw"
      >{{ $t('common.originalSize') }}</option>
      <option
        v-for="size in sizes"
        :value="size"
      >{{ size }}</option>
    </b-select>
    <div class="mt-2">
      <button
        class="button"
        @click="insertImage()"
      >
        <span class="icon">
          <i v-if="actionButtonType === 'copy'" class="fas fa-copy"></i>
          <i v-else class="fas fa-plus"></i>
        </span>
        <span v-if="actionButtonType === 'copy'">{{ $t('common.copy') }}</span>
        <span v-else>{{ $t('common.insertOf', {name: $t('common.image')}) }}</span>
      </button>
    </div>
  </div>

  <button
    class="button is-light is-small btn-delete"
    @click="deleteFile"
  >
    <span class="icon">
      <i class="fas fa-times-circle"></i>
    </span>
  </button>
  <b-loading :is-full-page="false" v-model="isUploading"></b-loading>
</div>
</template>
<script>
import axios from 'axios'
import { Admin } from '@/api'
import util from '@/util'
import FbImg from '@/components/atoms/FbImg'
import EbDropdown from '@/components/molecules/EbDropdown'

export default{
  name: 'FileUploaderImage',

  components: {
    FbImg,
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
      default: 'insert',
    },

    uploaderOptions: {
      type: Object,
      required: true,
      default: null,
    },
  },

  data(){
    return {
      WINDOW_URL: null,
      isUploading: false,
      caption: '',
      insertSize: 'raw',
      error: '',
    }
  },

  computed: {
    isFileObject() {
      return this.file instanceof File
    },

    sizes() {
      if (this.checkEmpty(this.uploaderOptions)) return []
      return this.uploaderOptions.sizes
    },
  },

  watch: {
    file(val) {
    }
  },

  created() {
    this.WINDOW_URL = (window.URL || window.webkitURL)
  },

  async mounted() {
    if (this.file.caption) this.caption = this.file.caption
    if (this.isFileObject) {
      this.setThumbToLocalImage()
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
          fileType: 'image',
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

    insertImage() {
      const imgUrl = this.mediaUrl('image', this.file.fileId, this.file.mimeType, this.insertSize)
      this.$emit('insert-image', { url:imgUrl, caption:this.caption })
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

    setThumbToLocalImage() {
      if ('thumb' in this.file && this.file.thumb) return

      // Create a blob field
      this.file.blob = ''
      if (this.WINDOW_URL) {
        this.file.blob = this.WINDOW_URL.createObjectURL(this.file)
      }
      // Thumbnails
      this.file.thumb = ''
      if (this.file.blob && this.file.type.substr(0, 6) === 'image/') {
        this.file.thumb = this.file.blob
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
.upload-image-box {
  position: relative;
}
.btn-delete {
  position: absolute;
  top: 10px;
  right: 10px;
}
</style>
