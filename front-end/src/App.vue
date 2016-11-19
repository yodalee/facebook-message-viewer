<template>
  <div>
    <div class="container">
      <div class="col-md-3 col-lg-2 col-lg-offset-1">
        <h2>Group List</h2>

        <ul v-if="groups.length > 0">
          <li v-for="group in groups" @click="show(group)">
            <group-item :member="group.split(/,/g)" :selected="group == display_group"></group-item>
          </li>
        </ul>
        <p v-else>No Groups Data</p>
      </div>

      <div class="col-md-9 col-lg-8">
        <div>
          <h2>Filter</h2>

          <date-picker class="datetime-picker" :option="date_picker_option('Since')" :date="startdate"></date-picker>
          <date-picker class="datetime-picker" :option="date_picker_option('Before')" :date="enddate"></date-picker>
          <button class="btn btn-info v-center" @click="show(display_group)">Apply filter</button>
        </div>

        <div>
          <h2>Message</h2>

          <div class="messages">
            <template v-if="state == 'standby'">
              <template v-if="display_group && messages[display_group]">
                <message v-for="msg in messages[display_group]" :message="msg"></message>
              </template>
              <p v-else>No message</p>
            </template>
            <p v-else>{{ state | help }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import request from 'superagent'
import GroupItem from 'components/GroupItem'
import Message from 'components/Message'

const API_BASE = 'http://localhost:8787'

Vue.filter('help', (state) => ({
  'loading': 'Loading...',
  'error': 'Server error'
})[state] || 'Unkown error'
)

export default {
  components: { GroupItem, Message },
  created () {
    this.state = 'loading'
    request.get(API_BASE + '/fetch').query({type: 'groups'}).end((err, res) => {
      if (err) {
        this.state = 'error'
        console.log('err')
      } else {
        this.state = 'standby'
        const data = JSON.parse(res.text)
        const groups = data.groups || []
        this.groups = groups
      }
    })
  },
  data () {
    return {
      state: 'standby',
      groups: [],
      messages: {},
      display_group: null,

      startdate: {
        time: ''
      },
      enddate: {
        time: ''
      }

    }
  },
  methods: {
    show (group) {
      this.state = 'loading'
      request
        .get(API_BASE + '/fetch')
        .query({
          type: 'message',
          group: group,
          startdate: this.startdate.time.replace(/-/g, ''),
          enddate: this.enddate.time.replace(/-/g, '')
        })
        .end((err, res) => {
          if (err) {
            this.state = 'error'
            console.log(err)
          } else {
            const data = JSON.parse(res.text)
            const messages = data.messages || []
            this.messages[group] = messages
            this.display_group = group
            this.state = 'standby'
          }
        })
    },
    date_picker_option (placeholder) {
      return {
        type: 'day',
        week: ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'],
        month: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
        format: 'YYYY-MM-DD',
        placeholder: placeholder,
        inputStyle: {
          'vertical-align': 'middle',
          'display': 'inline-block',
          'padding': '6px 12px',
          'line-height': '1.42857143',
          'font-size': '14px',
          'background-color': '#8444bf',
          'border': '1px solid #6114a9',
          'border-radius': '.2em',
          'color': '#ffffff',
          'cursor': 'pointer',
          'width': '8em',
          'text-align': 'center'
        },
        buttons: {
          ok: 'Ok',
          cancel: 'Cancel'
        },
        overlayOpacity: 0.5, // 0.5 as default
        dismissible: true // as true as default
      }
    }
  }
}
</script>

<style lang="scss" scoped>
ul {
  padding: 0;

  li {
    list-style: none;
    display: block;
  }
}

.v-center {
  vertical-align: middle;
}
</style>

<style lang="scss">
.datetime-picker{
  ::placeholder {
    color: #eee;
  }
}
</style>
