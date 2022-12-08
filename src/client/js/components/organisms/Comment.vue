<template>
<div>
  <p>{{ comment.body }}</p>
  <div>
    <time
      itemprop="datepublished"
      :datetime="comment.createdAt | dateFormat('')"
    >{{ comment.createdAt | dateFormat }}</time>
  </div>
  <vote-unit
    :vote-types="voteTypes"
    :posted-votes="postedVotes"
    :content-id="comment.commentId"
    @post-vote="postVote"
  ></vote-unit>
</div>
</template>
<script>
import config from '@/config/config'
import VoteUnit from '@/components/organisms/VoteUnit'

export default{
  name: 'CommentComponent',

  components: {
    VoteUnit,
  },

  props: {
    comment: {
      type: Object,
      required: true,
    },
    postedVotes: {
      type: Array,
    },
  },

  data(){
    return {
    }
  },

  computed: {
    voteTypes() {
      return config.voteTypesDefault
    },
  },

  watch: {
  },

  created() {
  },

  methods: {
    postVote(voteType) {
      const payload = {
        contentId: this.comment.commentId,
        voteType: voteType,
      }
      this.$emit('post-vote', payload)
    }
  },
}
</script>

