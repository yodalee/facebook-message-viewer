import Vue from 'vue'
import VueDatepicker from 'vue-datepicker'
import VueMoment from 'vue-moment'
import App from './App'

import 'bootstrap/dist/css/bootstrap.css'

Vue.use(VueMoment)
Vue.component('date-picker', VueDatepicker)

/* eslint-disable no-new */
new Vue({
  el: '#app',
  template: '<App/>',
  components: { App }
})
