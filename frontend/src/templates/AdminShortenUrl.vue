<template>
<div v-if="shortenUrl">
  <div class="block">
    <router-link :to="listPageUri">
      <i class="fas fa-chevron-left"></i>
      <span>{{ $t('page.ShortenUrlList') }}</span>
    </router-link>
  </div>

  <h1 class="title">{{ shortenUrl.urlId }}</h1>
  <h2 class="subtitle">{{ shortenUrl.name }}</h2>

  <div class="is-pulled-right">
    <eb-dropdown
      v-if="hasEditorRole"
      position="is-bottom-left"
    >
      <span
        slot="label"
        class="icon"
      >
        <i class="fas fa-edit"></i>
      </span>
      <div class="dropdown-content">
        <router-link
          :to="`/admin/shorten-urls/${serviceId}/${shortenUrl.urlId}/edit`"
          class="dropdown-item"
        >
          <span class="icon">
            <i class="fas fa-pen"></i>
          </span>
          <span>{{ $t('common.edit') }}</span>
        </router-link>

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

  <div class="field">{{ shortenUrl.description }}</div>

  <div class="mt-6">
    <div class="field">
      <label class="label">{{ $t('common.locationTo') }}</label>
      <div class="control">
        <a :href="shortenUrl.url" target="_blank">{{ shortenUrl.url }}</a>
      </div>
    </div>

    <div class="field mt-5">
      <label class="label">{{ $t('form.isViaJumpPageLabel') }}</label>
      <div
        v-text="shortenUrl.isViaJumpPage ? $t('form.viaJumpPage') : $t('form.notViaJumpPage')"
        class="control"
      ></div>
    </div>

    <div class="field">
      <label class="label">{{ $t('common.paramsFor', {target: $t('term.accessAnalysis')}) }}</label>
      <div
        v-if="shortenUrl.paramKey"
        v-text="`${shortenUrl.paramKey}=${shortenUrl.paramValue}`"
        class="control"
      ></div>
      <div
        v-else
        class="control"
      >{{ $t('msg.Unregistered') }}</div>
    </div>

    <div class="field mt-5">
      <label class="label">{{ $t('term.generatedUrl') }}</label>
      <div class="control is-size-5 u-wrap">
        <a :href="shortenUrl.locationTo" target="_blank">{{ shortenUrl.locationTo }}</a>
      </div>
    </div>
  </div>

  <div class="mt-6 p-4 has-background-light">
    <h3 class="title is-4">{{ $t('term.shortenUrl') }}</h3>
    <div><a
      :href="redirectUrl"
      class="is-size-5"
      target="_blank"
    >{{ redirectUrl }}</a></div>
    <div
      v-if="isDispQrCode"
      class="mt-3"
    >
      <div><img :src="qrCodeUrl"></div>
      <div class="mt-2"><a :href="qrCodeUrl" :download="`${urlId}.png`" target="_blank">{{ $t('common.download') }}</a></div>
    </div>
    <div
      class="mt-3 has-text-warning-dark"
      v-else-if="isLoading === false"
    >{{ $t('msg.generateItemRequiresTimes', { target: $t('common.images') }) }}</div>
  </div>

</div>
</template>
<script>
import config from '@/config/config'
import utilDate from '@/util/date'
import { Admin } from '@/api'
import EbDropdown from '@/components/molecules/EbDropdown'

export default{
  name: 'AdminShortenUrl',

  components: {
    EbDropdown,
  },

  data(){
    return {
      shortenUrl: null,
      isDispQrCode: false,
    }
  },

  computed: {
    urlId() {
      return this.$route.params.urlId
    },

    qrCodeUrl() {
      return `${config.media.url}/shorten-url/qrcodes/${this.shortenUrl.urlId}.png`
    },

    redirectUrl() {
      return `${config.shortenUrl.redirectBaseUrl}${this.urlId}`
    },

    listPageUri() {
      const uri = `/admin/shorten-urls/${this.serviceId}`

      if (!this.$store.state.adminShortenUrlsPager.lastIndex) return uri
      return `${uri}?index=${this.$store.state.adminShortenUrlsPager.lastIndex}`
    },
  },

  async created() {
    await this.getShortenUrl()
    this.displayQrCode()
  },

  methods: {
    async getShortenUrl() {
      this.shortenUrl = await Admin.getShortenUrls(this.serviceId, this.urlId, null, this.adminUserToken)
    },

    confirmDelete() {
      this.$buefy.dialog.confirm({
        message: this.$t('msg.cofirmToDelete'),
        onConfirm: async () => await this.deleteShortenUrl()
      })
    },

    async deleteShortenUrl() {
      try {
        this.$store.dispatch('setLoading', true)
        const res = await Admin.deleteShortenUrl(this.serviceId, this.urlId, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
        this.$router.push(`/admin/shorten-urls/${this.serviceId}`)
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        if (this.checkResponseHasErrorMessage(err, true)) {
          this.setErrors(err.response.data.errors)
        }
        this.handleApiError(err, this.$t(`msg["Delete failed"]`))
      }
    },

    displayQrCode() {
      const now = utilDate.nowUtime()
      const createdAt = utilDate.unixtimeFromStr(this.shortenUrl.createdAt)
      if (now - createdAt > config.shortenUrl.waitingTimeForQrCodeCreated) {
        this.isDispQrCode = true
        return
      }
      setTimeout(() => {
        this.isDispQrCode = true
      }, config.shortenUrl.waitingTimeForQrCodeCreated * 1000)
    },
  },
}
</script>

