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
  </div>

</div>
</template>
<script>
import moment from '@/moment'
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
    }
  },

  computed: {
    urlId() {
      return this.$route.params.urlId
    },

    listPageUri() {
      const uri = `/admin/shorten-urls/${this.serviceId}`

      if (!this.$store.state.adminShortenUrlsPager.lastIndex) return uri
      return `${uri}?index=${this.$store.state.adminShortenUrlsPager.lastIndex}`
    },
  },

  async created() {
    await this.getShortenUrl()
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
        const res = await Admin.deleteShortenUrl(this.urlId, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
        this.$router.push(`/admin/shorten-urls/${this.serviceId}`)
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

