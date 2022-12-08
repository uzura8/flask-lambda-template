import 'es6-promise/auto'
import Vue from 'vue'
import router from '@/router'
import i18n from '@/i18n'
import store from '@/store'
import cognito from './cognito'
import '@/sanitize'
import App from '@/App'

import Buefy from 'buefy'
Vue.use(Buefy)

import VueClipboard from 'vue-clipboard2'
Vue.use(VueClipboard)

import mixin from '@/mixins/site'
Vue.mixin(mixin);

import * as filters from '@/filters'
Object.keys(filters).forEach(key => {
  Vue.filter(key, filters[key]);
});

new Vue({
  el: '#app',
  router,
  store,
  i18n,
  cognito,
  render: h => h(App)
})
