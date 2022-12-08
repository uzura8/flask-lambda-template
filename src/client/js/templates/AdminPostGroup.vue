<template>
<div>
  <div class="block">
    <router-link :to="`/admin/posts/${serviceId}/groups`">
      <i class="fas fa-chevron-left"></i>
      <span>{{ $t('page.AdminPostGroupManagement') }}</span>
    </router-link>
  </div>

  <div v-if="postGroup">
    <h1 class="title">{{ $t('term.postGroup') }}</h1>
    <p class="subtitle is-5">{{ postGroupLabel }}</p>
  </div>

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
          :to="`/admin/posts/${serviceId}/groups/${slug}/edit`"
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
  <div class="mt-6">
    <span>
      <button
        class="button"
        @click="isPostModalActive = true"
      >
        <span class="icon">
          <i class="fas fa-plus"></i>
        </span>
        <span>{{ $t('common.addFor', { target:$t('common.post') }) }}</span>
      </button>
    </span>
    <b-modal
      v-model="isPostModalActive"
      :destroy-on-hide="false"
      aria-role="dialog"
      close-button-aria-label="Close"
      aria-modal
    >
      <template #default="props">
        <div class="modal-card" style="width: auto">
          <header class="modal-card-head">
            <p class="modal-card-title">
              {{ $t('common.selectFor', { target: $t('common.post') }) }}
            </p>
            <button
              type="button"
              class="delete"
              @click="isPostModalActive = false"
            ></button>
          </header>
          <section class="modal-card-body">
            <post-list
              list-type="simpleSelect"
              :selected-ids="postIds"
              @select="addGroupItem"
            ></post-list>
          </section>
          <footer class="modal-card-foot">
            <button
              class="button"
              type="button"
              @click="isPostModalActive = false"
            >{{ $t('common.close') }}</button>
          </footer>
        </div>
      </template>
    </b-modal>
  </div>
  <div class="mt-5" v-if="groupItems.length > 0">
    <draggable
      v-model="groupItems"
      :group="`postGroup-${slug}`"
      :options="{handle:'.handle'}"
      @start="drag=true"
      @end="drag=false"
    >
      <div
        v-for="post in groupItems"
        :key="post.postId"
        class="columns is-mobile is-vcentered is-1"
      >
        <div class="column is-1 is-size-6">
          <button class="button is-small handle">
            <span class="icon is-small">
              <i class="fas fa-sort"></i>
            </span>
          </button>
        </div>

        <div class="column is-size-6">
          <div>{{ post.title }}</div>
          <div class="is-size-7">
            <span>{{ $t('common.publishAt') }}</span>
            <span>{{ post.publishAt | dateFormat }}</span>
          </div>
        </div>

        <div class="column is-1 is-size-6">
          <button
            @click="deletePostGroupItem(post.postId)"
            class="button is-small"
          >
            <span class="icon is-small">
              <i class="fas fa-trash"></i>
            </span>
          </button>
        </div>
      </div>
    </draggable>
  </div>
  <div v-else class="mt-5">
    <p>{{ $t('msg["Data is empty"]') }}</p>
  </div>
</div>
</template>
<script>
import draggable from 'vuedraggable'
import { Admin } from '@/api'
import EbDropdown from '@/components/molecules/EbDropdown'
import PostList from '@/components/organisms/PostList'

export default{
  name: 'AdminPostGroup',

  components: {
    draggable,
    EbDropdown,
    PostList,
  },

  data(){
    return {
      postGroup: null,
      groupItems: [],
      isPostModalActive: false,
    }
  },

  computed: {
    postGroupLabel() {
      return this.postGroup.label
    },

    slug() {
      return this.$route.params.slug
    },

    postIds() {
      if (this.checkEmpty(this.groupItems) === true) return []
      return this.groupItems.map(item => item.postId)
    },
  },

  watch: {
    async postIds(vals, before) {
      if (this.checkEmpty(before) === false) {
        await this.updatePostGroup()
      }
    },
  },

  async created() {
    await this.setPostGroup()
  },

  methods: {
    async setPostGroup() {
      const params = { 'withPostDetail':1 }
      this.postGroup = await Admin.getPostGroups(this.serviceId, this.slug, params, this.adminUserToken)
      this.groupItems = this.postGroup.posts
    },

    addGroupItem(post) {
      if (this.postIds.includes(post.postId)) {
        this.showGlobalMessage(this.$t('msg.AlreadySet'))
        return
      }
      this.groupItems.push(post)
      this.isPostModalActive = false
    },

    deletePostGroupItem(postId) {
      const index = this.groupItems.findIndex(item => item.postId === postId)
      this.groupItems.splice(index, 1)
    },

    async updatePostGroup() {
      try {
        this.$store.dispatch('setLoading', true)
        const vals = { postIds: this.postIds }
        await Admin.updatePostGroup(this.serviceId, this.slug, vals, this.adminUserToken)
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        console.log(err);//!!!!!!
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t(`msg["Delete failed"]`))
      }
    },

    confirmDelete() {
      this.$buefy.dialog.confirm({
        message: this.$t('msg.cofirmToDelete'),
        onConfirm: async () => await this.deletePostGroup()
      })
    },

    async deletePostGroup() {
      try {
        this.$store.dispatch('setLoading', true)
        await Admin.deletePostGroup(this.serviceId, this.slug, this.adminUserToken)
        this.$emit('deleted', this.slug)
        this.$store.dispatch('setLoading', false)
        this.$router.push(`/admin/posts/${this.serviceId}/groups`)
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

