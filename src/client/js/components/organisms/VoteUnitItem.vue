<template>
<span>
  <a @click="vote(voteType)">
    <span class="icon is-small"><i :class="icon"></i></span>
  </a>
  <span class="ml-1">{{ voteCount | numFormat }}</span>
</span>
</template>
<script>
import { Vote } from '@/api'
import VoteUnit from '@/components/organisms/VoteUnit'

export default{
  name: 'Votes',

  components: {
    VoteUnit,
  },

  props: {
    contentId: {
      type: String,
      required: true,
    },

    voteType: {
      type: String,
      default: '',
    },

    voteCount: {
      type: Number,
      default: 0,
    },

    iconClass: {
      type: String,
      default: '',
    },
  },

  data(){
    return {
    }
  },

  computed: {
    icon() {
      if (this.iconClass) return this.iconClass

      switch (this.voteType) {
        case 'dislike':
          return 'fas fa-thumbs-down'

        case 'like':
        default:
          return 'fas fa-thumbs-up'
      }
    },
  },

  watch: {
  },

  created() {
  },

  methods: {
    vote(voteType) {
      this.$emit('post-vote', voteType)
    },
  },
}
</script>

