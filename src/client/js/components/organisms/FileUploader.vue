<template>
<div>
  <ul
    v-if="fileType === 'image'"
    class="columns is-multiline"
  >
    <li
      v-for="(file, index) in files"
      :key="file.fileId"
      class="column is-half-tablet is-one-third-desktop is-one-quarter-widescreen"
    >
      <file-uploader-image
        :file="file"
        :enable-caption="true"
        :action-button-type="imageActionButtonType"
        @uploaded-file="setUploadedFile"
        @delete-file="deleteFile"
        @input-caption="inputCaption"
        @insert-image="insertImage"
      ></file-uploader-image>
    </li>
  </ul>

  <ul
    v-else-if="fileType === 'file'"
    class="columns is-multiline"
  >
    <li
      v-for="(file, index) in files"
      :key="file.fileId"
      class="column is-half-desktop is-one-third-widescreen"
    >
      <file-uploader-file
        :file="file"
        :enable-caption="true"
        :action-button-type="fileActionButtonType"
        @uploaded-file="setUploadedFile"
        @delete-file="deleteFile"
        @input-caption="inputCaption"
        @copy-url="copyUrl"
      ></file-uploader-file>
    </li>
  </ul>

  <b-upload
    class="file-label"
    multiple
    :accept="getUploadConfig('mimeTypes', []).join(',')"
    @input="setFileId"
  >
    <span class="file-cta">
      <b-icon class="file-icon" pack="fas" icon="upload"></b-icon>
      <span class="file-label">{{ buttonLabel }}</span>
    </span>
  </b-upload>
</div>
</template>
<script>
import { ulid } from 'ulid'
import { Admin } from '@/api'
import config from '@/config/config'
import util from '@/util'
import FileUploaderImage from '@/components/organisms/FileUploaderImage'
import FileUploaderFile from '@/components/organisms/FileUploaderFile'

export default{
  name: 'FileUploader',

  components: {
    FileUploaderImage,
    FileUploaderFile,
  },

  props: {
    fileType: {
      type: String,
      required: true,
      default: 'image',
    },

    value: {
      type: Array,
      required: false,
      default: () => ([]),
    },

    imageActionButtonType: {
      type: String,
      required: false,
      default: 'insert',
    },

    fileActionButtonType: {
      type: String,
      required: false,
      default: 'copy',
    },
  },

  data(){
    return {
      files: [],
      uploaderOptions: null,
    }
  },

  computed: {
    buttonLabel() {
      const labelKey = this.fileType === 'image' ? 'form.SelectImages' : 'form.SelectFiles'
      return this.$t(labelKey)
    },
  },

  watch: {
    files(vals) {
      let inputVals = []
      vals.map((val) => {
        if (val instanceof File) return
        const payload = { fileId:val.fileId, mimeType:val.mimeType }
        if (val.caption) payload.caption = val.caption
        inputVals.push(payload)
      })
      if (inputVals) {
        this.$emit('input', inputVals)
      }
    },
  },

  created() {
    this.uploaderOptions = config.media.upload[this.fileType]
    if (this.value) {
      this.value.map((item) => {
        const item_copied = { ...item }
        item_copied.isSaved = true
        this.files.push(item_copied)
      })
    }
  },

  methods: {
    setUploadedFile(payload) {
      const index = this.files.findIndex((item) => {
        return item.fileId === payload.fileId
      })
      if (index === -1) return

      let sevedFile = {...payload}
      sevedFile.isUploaded = true
      sevedFile.originalName = this.files[index].name
      sevedFile.size = this.files[index].size
      this.files.splice(index, 1, sevedFile)
    },

    inputCaption(payload) {
      const index = this.files.findIndex((item) => {
        return item.fileId === payload.fileId
      })
      if (index === -1) return

      let sevedFile = { ...this.files[index] }
      sevedFile.caption = payload.caption
      this.files.splice(index, 1, sevedFile)
    },

    deleteFile(fileId) {
      const index = this.files.findIndex(item => item.fileId === fileId)
      this.files.splice(index, 1)
    },

    insertImage(payload) {
      this.$emit('insert-image', payload)
    },

    copyUrl(payload) {
      this.$emit('copy-url', payload)
    },

    setFileId(vals) {
      let index
      for (let i = 0, n = vals.length; i < n; i++) {
        if (! vals[i].fileId) {
          vals[i].fileId = ulid().toLowerCase()
        }
        index = this.files.findIndex(file => file.fileId === vals[i].fileId)
        if (index === -1) {
          this.files.push(vals[i])
        }
      }
    },

    getUploadConfig(key, defaultVal) {
      if (key in this.uploaderOptions) {
        return this.uploaderOptions[key]
      }
      return defaultVal
    },
  },
}
</script>

