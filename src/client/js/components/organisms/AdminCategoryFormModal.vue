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
      <admin-category-form
        :parent-category-slug-default="parentCategorySlug"
        :category="category"
        :is-modal-includes="true"
        @close="$emit('close')"
      ></admin-category-form>
    </section>
  </div>
</b-modal>
</template>
<script>
import AdminCategoryForm from '@/components/organisms/AdminCategoryForm'

export default {
  name: 'CategoryEditModal',

  components: {
    AdminCategoryForm,
  },

  props: {
    active: {
      type: Boolean,
      default: false,
    },

    parentCategorySlug: {
      type: String,
      default: '',
    },

   category: {
      type: Object,
      default: null,
    },
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
<style>
.modal-card {
  width: auto;
  min-width: 360px;
}
</style>
