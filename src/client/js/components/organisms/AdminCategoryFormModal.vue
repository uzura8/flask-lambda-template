<template>
<b-modal
  v-model="modalActive"
  has-modal-card
  trap-focus
  :destroy-on-hide="false"
  aria-role="dialog"
  aria-label="Example Modal"
  close-button-aria-label="Close"
  aria-modal
>
  <div class="modal-card" style="width: auto">
    <header class="modal-card-head">
      <p class="modal-card-title">
        {{ $t('common.addFor', {target: $t('common.category')}) }}
      </p>
      <button
        type="button"
        class="delete"
        @click="$emit('close')"
      />
    </header>
    <section class="modal-card-body">
        <b-field :label="$t('form.slug')">
          <b-input
            v-model="slug"
            type="text"
            required
          ></b-input>
        </b-field>

        <b-field :label="$t('form.label')">
          <b-input
            v-model="label"
            type="text"
            required
          ></b-input>
        </b-field>
    </section>
    <footer class="modal-card-foot">
      <b-button
        :label="$t('common.close')"
        @click="$emit('close')"
      />
      <b-button
        :label="$t('common.add')"
        type="is-primary"
      />
    </footer>
  </div>
</b-modal>
</template>

<script>
export default {
  name: 'CategoryEditModal',

  props: {
    active: {
      type: Boolean,
      default: false,
    }
  },

  data() {
    return {
      slug: '',
      label: '',
    }
  },

  computed: {
    modalActive: {
      get() {
        return this.active
      },
      set(data) {
        // childDataの値が更新されたら親のコンポーネントのupdate:parentDataを$emitで呼び出す
        // 親側に返すときはvue.jsの仕様でupdateイベントで返すと決まっている
        this.$emit('update:active', data);
      },
    },
  },

  watch: {
    active(val) {
      console.log([3332222, val]);//!!!!!!
    },
  },

  created() {
    console.log([333000, this.active]);//!!!!!!
  },
}
</script>
