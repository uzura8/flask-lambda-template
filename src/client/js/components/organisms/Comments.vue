<template>
<div>
  <ul v-if="comments.length > 0">
    <li
      v-for="comment in comments"
      class="block"
    >
      <comment-item
        :comment="comment"
        :posted-votes="votes.filter(vote => vote.contentId == comment.commentId)"
        @post-vote="postVote"
      ></comment-item>
    </li>
  </ul>

  <div v-else-if="!isLoading">
    <p>{{ $t('msg["Data is empty"]') }}</p>
  </div>

  <nav v-if="hasNext" class="u-mt2r">
    <a class="u-clickable" @click="fetchComments({ untilTime:lastItemCreatedAt })">{{ $t('common.more') }}</a>
  </nav>
</div>
</template>
<script>
import { Comment, Vote } from '@/api'
import CommentItem from '@/components/organisms/Comment'

export default{
  name: 'Comments',

  components: {
    CommentItem,
  },

  props: {
    contentId: {
      type: String,
      required: true,
    },
  },

  data(){
    return {
      comments: [],
      hasNext: false,
      listCount: 5,
      votes: [],
    }
  },

  computed: {
    category() {
      return this.$route.params.category
    },

    lastItemCreatedAt () {
      const lastIndex = this.comments.length - 1
      return this.comments.length > 0 ? encodeURI(this.comments[lastIndex].createdAt) : null
    },
  },

  watch: {
  },

  async created() {
    await this.fetchComments()
  },

  methods: {
    async fetchComments(params = {}, isLatest = false) {
      const params_copied = { ...params }
      params_copied.count = this.listCount + 1

      if (this.category) {
        params_copied.category = this.category
      }

      this.$store.dispatch('setLoading', true)
      try {
        let commentIds = []
        let items = await Comment.get(this.serviceId, this.contentId, params_copied)
        if (isLatest) {
          items.reverse()
        } else {
          if (items.length > this.listCount) {
            items.pop()
            this.hasNext = true
          } else {
            this.hasNext = false
          }
        }
        items.map(item => {
          if (isLatest) {
            this.comments.unshift(item)
          } else {
            this.comments.push(item)
          }
          commentIds.push(item.commentId)
        })
        await this.setCommentVotes(commentIds)
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        console.log(err);//!!!!!!
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    async setCommentVotes(commentIds) {
      if (!commentIds) return

      let params = {}
      if (commentIds.length > 0) {
        params.contentIds = commentIds.join(',')
      }
      this.votes = await Vote.get(this.serviceId, null, params)
    },

    async postVote(payload) {
      this.$store.dispatch('setLoading', true)
      try {
        const vals = { 'type': payload.voteType }
        const res = await Vote.post(this.serviceId, payload.contentId, vals)
        this.updateVotes(res)
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        console.log(err);//!!!!!!
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    updateVotes(updateds) {
      updateds.map((upd) => {
        const updContentIdType = [upd.contentId, upd.voteType].join('#')
        const index = this.votes.findIndex((item) => {
          const contentIdType = [item.contentId, item.voteType].join('#')
          return contentIdType === updContentIdType
        })
        if (index === -1) {
          this.votes.push(upd)
        } else {
          this.$set(this.votes, index, upd)
        }
      })
    },
  },
}
</script>

