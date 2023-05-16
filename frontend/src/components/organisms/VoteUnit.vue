<template>
<span>
  <vote-unit-item
    v-for="(voteType, index) in voteTypes"
    :key="voteType"
    :content-id="contentId"
    :vote-type="voteType"
    :vote-count="getVoteCount(voteType)"
    @post-vote="postVote"
    :class="index > 0 ? 'ml-4' : ''"
  ></vote-unit-item>
</span>
</template>
<script>
import VoteUnitItem from '@/components/organisms/VoteUnitItem'

export default{
  name: 'Votes',

  components: {
    VoteUnitItem,
  },

  props: {
    contentId: {
      type: String,
      required: true,
    },

    voteTypes: {
      type: Array,
      default: () => ([]),
    },

    postedVotes: {
      type: Array,
      default: () => ([]),
    },
  },

  data(){
    return {
    }
  },

  computed: {
  },

  watch: {
  },

  created() {
  },

  methods: {
    getVoteCount(voteType) {
      const vote = this.postedVotes.find((item) => {
        return item.voteType === voteType
      })
      return vote == null ? 0 : vote.voteCount
    },

    postVote(voteType) {
      this.$emit('post-vote', voteType)
    },
  },
}
</script>

