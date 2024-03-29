import store from '@/store'
import router from '@/router'
import cognito from '@/cognito'
import listener from '@/listener'
import util from '@/util'
import config from '@/config/config'

const isDebug = util.obj.getVal(config, 'isDebug', false)

export default {
  data(){
    return {
      globalError: '',
      errors: {},
    }
  },

  computed: {
    isLoading: function () {
      return this.$store.getters.isLoading()
    },

    isAdminPath: function () {
      return this.$route.path.startsWith('/admin')
    },

    isAdminUser() {
      return this.$store.getters.isAdminUser()
    },

    hasAdminRole() {
      return this.$store.getters.hasAdminRole()
    },

    checkAdminRole(role) {
      return this.$store.getters.checkAdminRole(role)
    },

    hasEditorRole() {
      return this.$store.getters.hasEditorRole()
    },

    adminRole() {
      return this.$store.getters.adminRole()
    },

    //adminUserAcceptServiceIds() {
    //  return this.$store.getters.adminUserAcceptServiceIds()
    //},

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
    checkEmpty: util.obj.isEmpty,
    checkObjHasProp: util.obj.checkObjHasProp,
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

    //usableTextSanitized: function (text) {
    //  let conved = util.str.nl2br(text)
    //  conved = util.str.url2link(conved)
    //  return this.$sanitize(conved)
    //},

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
      if (!publishAt || publishAt === 'None') return true

      const current = util.date.calcFromNow(3, 'seconds')
      return publishAt < current
    },

    getPostPublishStatus(postStatus, publishAt = '') {
      if (postStatus === 'unpublish') return 'unpublished'
      if (!publishAt) return 'published'

      const current = util.date.calcFromNow(3, 'seconds')
      return publishAt < current ? 'published' : 'reserved'
    },

    getCategoryLabel(slug) {
      const cates = this.$store.state.categoryItems
      if (this.checkEmpty(cates)) return ''
      const cate = cates.find(item => item.slug === slug)
      return cate != null ? cate.label : ''
    },

    getTokenExpirationTime(isFormat = false) {
      const utime = cognito.getTokenExpirationTime(this.adminUserToken)
      if (isFormat === false) return utime

      return util.date.localeStrFromUnixtime(utime)
    },

    async checkAndRefreshTokens() {
      if (cognito.checkTokenExpired(this.adminUserToken) === false) return

      const res = await this.refreshSession()
      if (res === false) {
        store.dispatch('setAdminUser', null)
        this.$router.push({
          path: '/signin',
          query: { redirect: this.$route.fullPath }
        })
      }
    },

    async refreshSession() {
      const username = this.adminUserName
      const refreshToken = this.$store.state.adminUser.refreshToken
      if (!username || !refreshToken) return false
      const session = await cognito.refreshSession(username, refreshToken)
      if (!session) return false
      
      store.dispatch('setAdminUserTokens', {
        idToken: session.getIdToken().getJwtToken(),
        accessToken: session.getAccessToken().getJwtToken(),
        refreshToken: session.getRefreshToken().getToken(),
      })
      return true
    },

    debugOutput(data) {
      if (isDebug === false) return
      console.log(data)
    },
  },
}
