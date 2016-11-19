import Vue from 'vue'
import VueMoment from 'vue-moment'
import App from './App'

import 'bootstrap/dist/css/bootstrap.css'

Vue.use(VueMoment)

/* eslint-disable no-new */
new Vue({
  el: '#app',
  template: '<App/>',
  components: { App }
})
