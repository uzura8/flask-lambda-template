import moment from '@/moment'
import store from '@/store'
import router from '@/router'
import listener from '@/listener'
import util from '@/util'
import config from '@/config/config'

export default {
  data(){
    return {
      globalError: '',
      errors: {},
    }
  },

  computed: {
    isLoading: function () {
      return this.$store.state.common.isLoading
    },

    isAdminPath: function () {
      return this.$route.path.startsWith('/admin')
    },

    isAdminUser() {
      return this.$store.getters.isAdminUser()
    },

    hasAdminRole() {
      if (this.isAdminUser === false) return false
      if (this.$store.state.adminUser == null) return false
      if ('attributes' in this.$store.state.adminUser === false) return false
      if ('role' in this.$store.state.adminUser.attributes === false) return false
      return this.$store.state.adminUser.attributes.role === 'admin'
    },

    adminUserAcceptServiceIds() {
      return this.$store.getters.adminUserAcceptServiceIds()
    },

    adminUserToken() {
      return this.$store.state.adminUser.token
    },

    adminUserName() {
      return this.$store.state.adminUser.username
    },

    isAuth: function () {
      return false
    },

    serviceId() {
      return this.$route.params.serviceId
    },
  },

  methods: {
    siteUri: util.site.uri,
    checkEmpty: util.common.isEmpty,
    inArray: util.arr.inArray,
    listenComponent: listener.listen,
    destroyedComponent: listener.destroyed,
    checkResponseHasErrorMessage: util.site.checkResponseHasErrorMessage,

    mediaUrl: function(type, fileId, mimeType, size='raw') {
      const ext = util.media.getExtensionByMimetype(mimeType)
      let pathItems = [config.media.url, this.serviceId]
      if (type === 'image') {
        const fileName = `${size}.${ext}`
        pathItems.push('images', fileId, fileName)
      } else {
        const fileName = `${fileId}.${ext}`
        pathItems.push('docs', fileName)
      }
      return pathItems.join('/')
    },

    showGlobalMessage: function(msg, type='is-danger', pos='is-bottom', duration=5000) {
      this.$buefy.toast.open({
        message: msg,
        type: type,
        duration: duration,
        position: pos,
      })
    },

    handleApiError: function(err, defaultMsg='', isRedirect = false) {
      if (isRedirect && err != null && err.response != null) {
        if (err.response.status == 401) {
          store.dispatch('resetAuth')
          this.$router.push({
            path: '/signin',
            query: { redirect: this.$route.fullPath }
          })
          return
        } else if (err.response.status == 403) {
          this.$router.push('/error/forbidden')
          return
        } else if (err.response.status == 404) {
          this.$router.push('/error/notfound')
          return
        }
      }
      if (typeof this.setErrors == 'function'
        && util.site.checkResponseHasErrorMessage(err, true)) {
        this.setErrors(err.response.data.errors)
      }
      if (util.site.checkResponseHasErrorMessage(err)) {
        const msg = err.response.data.message in this.$t('msg')
          ? this.$t(`msg["${err.response.data.message}"]`)
          : err.response.data.message
        this.showGlobalMessage(msg)
      } else if (defaultMsg) {
        this.showGlobalMessage(defaultMsg)
      } else {
        this.showGlobalMessage(this.$t('msg["Server error"]'))
      }
    },

    usableTextSanitized: function (text) {
      let conved = util.str.nl2br(text)
      conved = util.str.url2link(conved)
      return this.$sanitize(conved)
    },

    usableTextEscaped: function (text) {
      let conved = util.str.escapeHtml(text)
      conved = util.str.nl2br(conved)
      return util.str.url2link(conved)
    },

    convUserTypeToi18n: function (user) {
      if (user.isAdmin) return this.$t('common.admin')
      if (user.isAnonymous) return this.$t('common.anonymous')

      return this.$t('common.normal')
    },

    setErrors: function(errors) {
      errors.map(err => {
        const field = util.str.convSnakeToCamel(err.field)
        this.initError(field)
        const msg = err.message in this.$t('msg')
          ? this.$t(`msg["${err.message}"]`)
          : err.message
        this.errors[field].push(msg)
      })
    },

    moveToErrorPage: function(code) {
      if (code == 404) {
        router.push({ path: '/notfound' })
      }
    },

    initError: function(field) {
      this.globalError = ''
      this.$set(this.errors, field, [])
    },

    initErrors: function() {
      this.globalError = ''
      Object.keys(this.errors).map(field => {
        this.initError(field)
      })
    },

    checkPostPublished(postStatus, publishAt = '') {
      if (postStatus === 'unpublish') return false
      if (!publishAt) return true

      const current = moment.utc().add(3, 'seconds').format()
      return publishAt < current
    },

    getPostPublishStatus(postStatus, publishAt = '') {
      if (postStatus === 'unpublish') return 'unpublished'
      if (!publishAt) return 'published'

      const current = moment.utc().add(3, 'seconds').format()
      return publishAt < current ? 'published' : 'reserved'
    },
  },
}
